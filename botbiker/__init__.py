import plugins, logging, time, asyncio, aiohttp, time, math, sys
logger = logging.getLogger(__name__)

headers={
  "Client-Identifier": "d49ae356392aebe31cb0d238e4311041",
}
_stations = None
_last_updated = 0

def _initialise(bot):
    plugins.register_user_command(["locknearme", "bikenearme"])

@asyncio.coroutine
def get_stations():
    global _stations, _last_updated

    now = time.time()
    if _stations is not None and now - last_updated < 1000*60:
        return _stations

    r = yield from aiohttp.request("get", "https://oslobysykkel.no/api/v1/stations", headers=headers)
    tmp = yield from r.json()
    _stations = tmp["stations"]
    _last_updated = time.time()
    return _stations

def calc_distance(loc0, loc1):
    t0 = math.radians(loc0[0])
    t1 = math.radians(loc1[0])
    d0 = math.radians(loc1[1]-loc0[1])
    return math.acos( math.sin(t0)*math.sin(t1) + math.cos(t0)*math.cos(t1) * math.cos(d0) ) * 6371e3

def get_station_near(location, fn):
    stations = yield from get_stations()
    fn = fn if fn is not None else lambda x: True

    nearest = None
    nearest_dist = sys.maxsize

    for station in stations:
        center = station["center"]
        distance = calc_distance([center["latitude"], center["longitude"]], location)
        if distance < nearest_dist and fn(station):
            nearest = station

    return nearest

def find_bike(bot, event, fn):
    try:
        success, location = bot.call_shared("where.ami", bot, event.user)
    except:
        yield from bot.coro_send_message(event.conv_id, "I depend on 'whereto' to werk, pliz tell Alex to load it")

    if success:
        tmp = location.split(",")
        location = [float(tmp[0]), float(tmp[1])]
        tmp = yield from get_station_near(location, fn)
        return tmp
    else:
        yield from bot.coro_send_message(event.conv_id, "I duno where you are, pliz share location")
        return None

def get_availability():
    r = yield from aiohttp.request("get", "https://oslobysykkel.no/api/v1/stations/availability", headers=headers)
    tmp = yield from r.json()
    return tmp["stations"]

def locknearme(bot, event, *args):
    availability = yield from get_availability()

    def has_locks(station):
        for av_station in availability:
            if av_station["id"] == station["id"]:
                if av_station["availability"]["locks"] > 0:
                    return True
        return False

    station = yield from find_bike(bot, event, has_locks)
    if station is None:
        yield from bot.coro_send_message(event.conv_id, "No nearby locks avaliable :(")
        return
    yield from bot.coro_send_message(event.conv_id, station["title"])

def bikenearme(bot, event, *args):
    availability = yield from get_availability()

    def has_bikes(station):
        for av_station in availability:
            if av_station["id"] == station["id"]:
                if av_station["availability"]["bikes"] > 0:
                    return True
        return False

    station = yield from find_bike(bot, event, has_bikes)
    if station is None:
        yield from bot.coro_send_message(event.conv_id, "No nearby bikes avaliable :(")
        return
    yield from bot.coro_send_message(event.conv_id, station["title"])
