import plugins, logging, time, asyncio, aiohttp, time, math, sys, re
from xml.etree import ElementTree
logger = logging.getLogger(__name__)

def _initialise(bot):
    plugins.register_handler(quick_forecast, type="message", priority=5)
    plugins.register_user_command(["forecast"])

def quick_forecast(bot, event, command):
    text_lower = event.text.lower()
    if "weather" in text_lower:
        match = re.search(r"\#(\w*)weather", text_lower)
        if match is not None:
            yield from forecast(bot, event, *["today", match.group(1)])


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
    today_only = False
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
        if len(args) > 1 and args[0].lower().strip() == "today":
            today_only = True
            args = args[1:]

        location = yield from get_location_by_search(" ".join(args))
        if location is None:
            yield from bot.coro_send_message(event.conv_id, "I duno where {0} is".format(" ".join(args)))
            return

    country = location.find("countryName")
    county = location.find("adminName1")
    municipality = location.find("adminName2")
    place = location.find("name")
    if municipality is None or municipality.text is None:
        municipality = place
    if county is None or county.text is None:
        county = place

    url_p = "{0}/{1}/{2}/{3}".format(country.text, county.text, municipality.text, place.text)
    url = "http://www.yr.no/place/{0}/forecast.xml".format(url_p)
    r = yield from aiohttp.request("get", url)
    tmp = yield from r.text()
    forecast = ElementTree.fromstring(tmp).find("forecast")
    if forecast is None:
        yield from bot.coro_send_message(event.conv_id, "Failed to find weather data for " + url_p)
        return

    time_line = forecast.find("text").find("location").findall("time")
    days = [time.find("title").text for time in time_line]
    day_index = 0

    tab_time_line = forecast.find("tabular").findall("time")

    message = "<b>"+place.text+"</b>\n"
    message += "<b>"+days[day_index]+"</b>\n"
    for time in tab_time_line:
        time_slot = ""
        period = time.attrib["period"]
        if period == "0":
            time_slot = "kl 00-06"
        elif period == "1":
            time_slot = "kl 06-12"
        elif period == "2":
            time_slot = "kl 12-18"
        elif period == "3":
            time_slot = "kl 18-24"

        message += "<b>"+time_slot+"</b> " + time.find("symbol").attrib["name"] + " " + time.find("temperature").attrib["value"] + "℃\n"

        if period == "3":
            yield from bot.coro_send_message(event.conv_id, message)
            if today_only:
                break
            day_index += 1
            if day_index >= len(days):
                break
            message = "<b>"+days[day_index]+"</b>\n"
