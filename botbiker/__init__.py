import plugins, logging, time, asyncio, aiohttp, time, math, sys
logger = logging.getLogger(__name__)

headers={
  "Client-Identifier": "d49ae356392aebe31cb0d238e4311041",
}
_stations = None
_last_station_updated = 0

def _initialise(bot):
    plugins.register_user_command(["locknearme", "bikenearme", "locksnearme", "bikesnearme"])

@asyncio.coroutine
def get_stations():
    global _stations, _last_station_updated

    now = time.time()
    if _stations is not None and now - _last_station_updated < 1000*60:
        return _stations

    r = yield from aiohttp.request("get", "https://oslobysykkel.no/api/v1/stations", headers=headers)
    tmp = yield from r.json()
    _stations = tmp["stations"]
    _last_updated = time.time()
    return _stations

def get_availability():
    r = yield from aiohttp.request("get", "https://oslobysykkel.no/api/v1/stations/availability", headers=headers)
    tmp = yield from r.json()
    return tmp["stations"]

def calc_distance(loc0, loc1):
    t0 = math.radians(loc0[0])
    t1 = math.radians(loc1[0])
    d0 = math.radians(loc1[1]-loc0[1])
    return math.acos( math.sin(t0)*math.sin(t1) + math.cos(t0)*math.cos(t1) * math.cos(d0) ) * 6371e3

def get_station_near(location, fn, limit, max_distance):
    stations = yield from get_stations()
    fn = fn if fn is not None else lambda x: True

    nearest = [x for x in stations if fn(x)]
    def distance(station):
        if "distance" in station:
            return station["distance"]
        center = station["center"]
        station["distance"] = calc_distance([center["latitude"], center["longitude"]], location)
        return station["distance"]

    nearest = [x for x in nearest if distance(x) < max_distance]
    limit = limit if limit < len(nearest) else len(nearest)
    return sorted(nearest, key=lambda station: distance(station))[:limit]

def find_bikes(bot, event, fn, limit=10, max_distance=1000):
    try:
        success, location = bot.call_shared("where.ami", bot, event.user)
    except:
        yield from bot.coro_send_message(event.conv_id, "I depend on 'whereto' to werk, pliz tell Alex to load it")
        return None

    if success:
        tmp = location.split(",")
        location = [float(tmp[0]), float(tmp[1])]
        tmp = yield from get_station_near(location, fn, limit, max_distance)
        return tmp
    else:
        yield from bot.coro_send_message(event.conv_id, "I duno where you are, pliz share location")
        return None

def nearme(bot, event, name, limit=4, max_distance=400):
    availability = yield from get_availability()

    avaliable_hash = {}
    def has_avaliable(station):
        for av_station in availability:
            if av_station["id"] == station["id"]:
                avaliable_hash[station["id"]] = av_station["availability"]
                if av_station["availability"][name+"s"] > 0:
                    return True
        return False

    stations = yield from find_bikes(bot, event, has_avaliable, limit, max_distance)
    if stations is None or len(stations) == 0:
        yield from bot.coro_send_message(event.conv_id, "No nearby "+name+"s avaliable :(")
        return

    for station in stations:
        message = "<b>" + str(avaliable_hash[station["id"]][name+"s"]) + "</b> "+name + ("s" if avaliable_hash[station["id"]][name+"s"] > 1 else "") + " at"
        message += " <b>" + station["title"] + "</b> " + station["subtitle"]
        message += " <i>" + ("%0.2f" % station["distance"]) + "m away</i>"
        yield from bot.coro_send_message(event.conv_id, message)

def locknearme(bot, event, *args):
    yield from nearme(bot, event, "lock", 1)

def bikenearme(bot, event, *args):
    yield from nearme(bot, event, "bike", 1)

def locksnearme(bot, event, *args):
    yield from nearme(bot, event, "lock", 5)

def bikesnearme(bot, event, *args):
    yield from nearme(bot, event, "bike", 5)
