import plugins, logging, time, asyncio, aiohttp, time, math, sys
from xml.etree import ElementTree
logger = logging.getLogger(__name__)

def _initialise(bot):
    plugins.register_user_command(["forecast"])

def get_location(geo_id):
    url = "http://api.geonames.org/get?geonameId={0}&username=jkrmc12".format(geo_id)
    r = yield from aiohttp.request("get", url)
    tmp = yield from r.text()
    return ElementTree.fromstring(tmp)

def get_location_by_search(query):
    url = "http://api.geonames.org/search?q={0}&maxRows=1&username=jkrmc12".format(query)
    r = yield from aiohttp.request("get", url)
    tmp = yield from r.text()
    root = ElementTree.fromstring(tmp)
    geo_name = root.find("geoname")
    if geo_name is None:
        return None
    geo_id = geo_name.find("geonameId")
    if geo_id is None:
        return None
    loc = yield from get_location(int(geo_id.text))
    return loc

def get_location_by_geo(lnglat):
    ll_tmp = lnglat.split(",")
    url = "http://api.geonames.org/findNearbyPlaceName?lat={0}&lng={1}&username=jkrmc12".format(float(ll_tmp[0]), float(ll_tmp[1]))
    r = yield from aiohttp.request("get", url)
    tmp = yield from r.text()
    root = ElementTree.fromstring(tmp)
    geo_name = root.find("geoname")
    if geo_name is None:
        return None
    geo_id = geo_name.find("geonameId")
    if geo_id is None:
        return None
    loc = yield from get_location(int(geo_id.text))
    return loc

def forecast(bot, event, *args):
    if event.user.is_self:
        return

    if len(args) == 0:
        yield from bot.coro_send_message(event.conv_id, "I duno where you want forecast ¯\\\_(ツ)_/¯")
        return

    location = None
    if args[0].lower().strip() == "here":
        try:
            success, lnglat = bot.call_shared("where.ami", bot, event.user)
        except:
            yield from bot.coro_send_message(event.conv_id, "I depend on 'whereto' to werk, pliz tell Alex to load it")
            return None

        if success:
            location = yield from get_location_by_geo(lnglat)
            if location is None:
                yield from bot.coro_send_message(event.conv_id, "I failed to find u, bro")
                return
        else:
            yield from bot.coro_send_message(event.conv_id, "I duno where you are, plz share location")
            return
    else:
        location = yield from get_location_by_search(" ".join(args))
        if location is None:
            yield from bot.coro_send_message(event.conv_id, "I duno where {0} is".format(" ".join(args)))
            return

    country = location.find("countryName")
    county = location.find("adminName1")
    municipality = location.find("adminName2")
    place = location.find("name")
    if municipality is None:
        municipality = place
    if county is None:
        county = place

    url_p = "{0}/{1}/{2}/{3}".format(country.text, county.text, municipality.text, place.text)
    url = "http://www.yr.no/place/{0}/forecast.xml".format(url_p)
    r = yield from aiohttp.request("get", url)
    tmp = yield from r.text()
    forecast = ElementTree.fromstring(tmp).find("forecast")
    if forecast is None:
        yield from bot.coro_send_message(event.conv_id, "Failed to find waether data for " + url_p)
        return

    time_line = forecast.find("text").find("location").findall("time")
    for time in time_line:
        message = "<b>"+time.find("title").text+"</b> "+ time.find("body").text
        yield from bot.coro_send_message(event.conv_id, message)
