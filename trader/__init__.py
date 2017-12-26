import plugins, logging, time, asyncio, aiohttp, math, sys
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except:
    logger.warn('install matplotlib with agg backend to generate plots')

_crypto_symbols = None
_crypto_map = None
crypto_symbols_last_update = 0
conv_symbols = ['EUR', 'USD', 'BTC']

gt_op = ['gt', '>', 'gtr', 'greater']
lt_op = ['lt', '<', 'lss', 'less']
def doop(a, b, op):
    if op in gt_op:
        return float(a) > float(b)
    elif op in lt_op:
        return float(a) < float(b)
    else:
        return float(a) == float(b)

def _initialise(bot):
    plugins.register_user_command(["trader"])
    plugins.start_asyncio_task(tick)

def print_help(bot, event, cmd):
    try:
        yield from bot.coro_send_message(event.conv_id, getattr(sys.modules[__name__], cmd).__doc__)
    except AttributeError:
        yield from bot.coro_send_message(event.conv_id, trader.__doc__)

def trader(bot, event, *args):
    """
    /bot trader <command> [arguments]
    Avaliable commands: alert, alertlist, coin

    For more details use
    /bot trader help <command>
    """
    if len(args) == 0 or args[0].lower() == 'help':
        yield from print_help(bot, event, 'trader' if len(args) < 2 else args[1])
        return

    cmd = args[0].lower()
    if cmd not in ['alert', 'coin', 'alertlist']:
        yield from print_help(bot, event, 'trader' if len(args) < 2 else args[1])
    else:
        yield from getattr(sys.modules[__name__], cmd)(bot, event, args[1:])


def alert(bot, event, args):
    """
    Create price new price alert (default price in EUR)
    /bot trader alert <coin> <operator> <price> [conv. currency]

    Example:
    /bot trader alert BTC less 10000 USD
    /bot trader alert LTC greater 300 EUR
    """

    if len(args) < 3:
        yield from print_help(bot, event, 'alert')
        return

    scoin = args[0]
    op = args[1].lower()
    price = args[2]
    conv = args[3].upper() if len(args) > 3 and args[3].upper() in conv_symbols else 'EUR'

    if op in gt_op:
        op = gt_op[0]
    elif op in lt_op:
        op = lt_op[0]
    else:
        yield from bot.coro_send_message(event.conv_id, 'Unknown operator {0}'.format(op))
        return

    symbols, cmap = yield from crypto_symbols()
    if scoin.upper() not in symbols:
        scoin = yield from coin_search(scoin)

    if scoin is None:
        yield from bot.coro_send_message(event.conv_id, 'Failed to find: {0}'.format(scoin))

    scoin = scoin.upper()
    if not bot.memory.exists(["traderalert"]):
        bot.memory["traderalert"] = {}

    alerts = bot.memory.get("traderalert")
    userid = event.user.id_.chat_id
    if userid in alerts:
        useralerts = alerts[userid]
    else:
        useralerts = []

    useralerts.append({
        'name': '{0}-{1}'.format(scoin, len(useralerts)+1),
        'sym': scoin,
        'conv': conv,
        'price': price,
        'op': op
    })

    alerts[userid] = useralerts
    bot.memory["traderalert"] = alerts
    bot.memory.save()
    yield from bot.coro_send_message(event.conv_id, 'New price alert created!')

def coin(bot, event, args):
    """
    Get coin info
    /bot trader coin <coin> [conv. currency]
    """
    if len(args) == 0:
        yield from print_help(bot, event, 'coin')
        return

    scoin = args[0]
    conv = args[1].upper() if len(args) > 1 and args[1].upper() in conv_symbols else 'EUR'

    symbols, cmap = yield from crypto_symbols()
    if scoin.upper() not in symbols:
        scoin = yield from coin_search(scoin)

    if scoin is None:
        yield from bot.coro_send_message(event.conv_id, 'Failed to find: {0}'.format(scoin))

    scoin = scoin.upper()#
    r = yield from aiohttp.request('get', 'https://min-api.cryptocompare.com/data/pricemultifull?fsyms={0}&tsyms={1}'.format(scoin, conv))
    r_json = yield from r.json()
    if 'Response' in r_json and r_json['Response'] == 'Error':
        yield from bot.coro_send_message(event.conv_id, 'API is broke\n{0}'.format(r_json['Message']))
        return

    data = r_json['DISPLAY'][scoin][conv]
    coin_data = cmap[scoin]
    yield from bot.coro_send_message(event.conv_id,
        '{0} last 24h\n<b>High:\t\t</b>{2}\n<b>Low:\t\t\t</b>{3}\n<b>Change:\t\t</b>{4} ({5}%)\n<b>Price:\t\t</b>{6}'.format(
            coin_data['FullName'], conv, data['HIGH24HOUR'], data['LOW24HOUR'], data['CHANGE24HOUR'], data['CHANGEPCT24HOUR'], data['PRICE']))

def alertlist(bot, event, args):
    """
    Manage price alerts
    /bot trader alertlist [remove] [list items]
    """
    if not bot.memory.exists(["traderalert"]):
        bot.memory["traderalert"] = {}

    alerts = bot.memory.get("traderalert")
    userid = event.user.id_.chat_id
    if userid not in alerts or len(alerts[userid]) == 0:
        yield from bot.coro_send_message(event.conv_id, 'You have no alerts')
        return

    useralerts = alerts[userid]
    if len(args) >= 2 and args[0] == 'remove':
        alerts[userid] = list(filter(lambda x: x['name'] not in args[1:], useralerts))
        bot.memory["traderalert"] = alerts
        bot.memory.save()
        yield from bot.coro_send_message(event.conv_id, 'Alerts updated')
        return
    else:
        yield from bot.coro_send_message(event.conv_id, '\n'.join([
            '<b>Name:</b> <i>{0}</i>\n<b>Watch:</b> {1} {2} {3} {4}\n'.format(
                alert['name'], alert['sym'], alert['op'], alert['price'], alert['conv'])
            for alert in useralerts
        ]))

@asyncio.coroutine
def coin_search(sstring):
    symbols, cmap = yield from crypto_symbols()

    rsym = None
    rlike = 0
    for sym, val in cmap.items():
        likenss = SequenceMatcher(None, sym, sstring.upper()).ratio()
        if likenss > rlike:
            rlike = likenss
            rsym = sym

        likenss = SequenceMatcher(None, val['CoinName'].lower(), sstring.lower()).ratio()
        if likenss > rlike:
            rlike = likenss
            rsym = sym

    if rlike < 0.6:
        return None

    return rsym

#def upload_plot():
#    pass

@asyncio.coroutine
def crypto_symbols():
    global _crypto_symbols, _crypto_map, crypto_symbols_last_update

    now = time.time()
    if _crypto_symbols is not None and now - crypto_symbols_last_update < 1000*60:
        return _crypto_symbols, _crypto_map

    r = yield from aiohttp.request('get', 'https://www.cryptocompare.com/api/data/coinlist/')
    r_json = yield from r.json()

    _crypto_symbols = r_json['Data'].keys()
    _crypto_map = r_json['Data']

    crypto_symbols_last_update = time.time()
    return _crypto_symbols, _crypto_map

@asyncio.coroutine
def tick(bot):
    while True:
        if not bot.memory.exists(["traderalert"]):
            bot.memory["traderalert"] = {}

        alerts = bot.memory.get("traderalert")
        coins = {}
        for userid, ualerts in alerts.items():
            for v in ualerts:
                if v['sym'] not in coins:
                    coins[v['sym']] = [v['conv']]
                elif v['conv'] not in coins[v['sym']]:
                    coins[v['sym']].append(v['conv'])

        if len(coins.items()) == 0:
            yield from asyncio.sleep(10)
            continue

        exchange = {}
        for sym, convs in coins.items():
            r = yield from aiohttp.request('get',
                'https://min-api.cryptocompare.com/data/price?fsym={0}&tsyms={1}'.format(
                    sym, ','.join(convs)
                ))
            resp = yield from r.json()
            if 'Response' in resp and resp['Response'] == 'Error':
                logger.error(resp['Message'])
                continue
            exchange[sym] = resp

        copy_alerts = alerts
        for userid, ualerts in alerts.items():
            for alert in ualerts:
                ext = exchange[alert['sym']]
                if doop(ext[alert['conv']], alert['price'], alert['op']):
                    copy_alerts[userid] = list(filter(lambda x: x['name'] != alert['name'], copy_alerts[userid]))
                    conv_1on1 = yield from bot.get_1to1(userid)
                    yield from bot.coro_send_message(conv_1on1,
                        'Alert! alarm for {0} {1} {2} {3}\nPrice: {4} {3}'.format(
                        alert['sym'], alert['op'], alert['price'], alert['conv'], ext[alert['conv']]))

        bot.memory["traderalert"] = copy_alerts
        bot.memory.save()
        yield from asyncio.sleep(60)
