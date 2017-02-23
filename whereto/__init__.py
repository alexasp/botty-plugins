import asyncio, aiohttp, re, os
import plugins
import logging
import random
import io

logger = logging.getLogger(__name__)
api_key = "AIzaSyDdGWh2QwcYHLEJOQGwKejtHY-PUC_5znc"

base_url_radar      = "https://maps.googleapis.com/maps/api/place/radarsearch/json"
base_url_details    = "https://maps.googleapis.com/maps/api/place/details/json"

oslo_latlng = "59.913869,10.752245"
radius      = "4000" #4km

user_location_map = {}

def _initialise(bot):
	plugins.register_handler(update_location, type="message", priority=5)
	plugins.register_user_command(["whereto"])
	bot.register_shared("where.ami", where_am_i)
	bot.register_shared("where.placeat", get_place_at)

def where_am_i(bot, user):
	if user.id_.chat_id in user_location_map:
		return True, user_location_map[user.id_.chat_id]
	else:
		return False, ''
	
def update_location(bot, event, command):
    if event.user.is_self:
        return

    if "maps.google.com" in event.text:
        logger.info(event.text)
        tmp = event.text.split("?q=")[1].split("@")
        user_location_map[event.user.id_.chat_id] = tmp[len(tmp)-1] 
        yield from bot.coro_send_message(event.conv_id, "I now know where " + event.user.full_name + " is ( ͡° ͜ʖ ͡°)")

def get_place_at(bot, location, type):
	url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
	url += "?location=" + location
	url += "&radius=20"
	url += "&key=" + api_key

	logger.info(url)
	r = yield from aiohttp.request('get', url)
	r_json = yield from r.json()
	if len(r_json["results"]) == 0:
		return False, '', '', None
	
	place = r_json["results"][0]

	url = base_url_details
	url += '?placeid=' + place["place_id"]
	url += '&key=' + api_key

	r = yield from aiohttp.request("get", url)
	r_json = yield from r.json()
	place = r_json["result"]
	
	image_data, filename = yield from get_map(bot, place["geometry"]["location"])
	image_id = yield from bot._client.upload_image(image_data, filename=filename)
	
	return True, place["name"], place["url"], image_id
		
def get_map(bot, latlng):
    url = "https://maps.googleapis.com/maps/api/staticmap"
    url += "?center=" + str(latlng["lat"]) + "," + str(latlng["lng"]) + "&zoom=18"
    url += "&size=400x400"
    url += "&format=jpg"
    url += "&markers=color:red%7Clabel:%7C" + str(latlng["lat"]) + "," + str(latlng["lng"])
    url += "&key=" + api_key

    filename = os.path.basename(url) + ".jpg"
    r = yield from aiohttp.request('get', url)
    raw = yield from r.read()
    return io.BytesIO(raw), filename

def maybedrink(bot, event, location):
	try: 
		success, name, image_id = yield from bot.call_shared("mixme.here", bot, str(location["lat"]) + "," + str(location["lng"]))
		if success:
			yield from bot.coro_send_message(event.conv_id, ".. and we can have a <b>" + name + "</b>", image_id=image_id)
		else:
			logger.info('found no drink here')
	except Exception as e:
		logger.info(e)
		logger.info('mixme plugin not loaded')
	
def query(bot, event, qtype, args):
	location = oslo_latlng
	rad = radius
	if args[0].lower().strip() == "nearby":
		if event.user.id_.chat_id not in user_location_map:
			yield from bot.coro_send_message(event.conv_id, "I don't know where " + event.user.full_name + " is, please share location.")
			return
		rad = "600"
		location = user_location_map[event.user.id_.chat_id]

	url = base_url_radar
	url += '?location=' + location
	url += '&radius=' + rad
	url += '&type=' + qtype
	url += '&key=' + api_key

	logger.info(url)

	r = yield from aiohttp.request("get", url)
	r_json = yield from r.json()

	if len(r_json["results"]) == 0:
		yield from bot.coro_send_message(event.conv_id, "No hits.")
		return

	place = r_json["results"][random.randint(0,len(r_json["results"])-1)]

	url = base_url_details
	url += '?placeid=' + place["place_id"]
	url += '&key=' + api_key

	r = yield from aiohttp.request("get", url)
	r_json = yield from r.json()
	place = r_json["result"]

	link = place["url"]
	name = place["name"]
	addr = place["vicinity"]

	image_data, filename = yield from get_map(bot, place["geometry"]["location"])
	image_id = yield from bot._client.upload_image(image_data, filename=filename)
	yield from bot.coro_send_message(event.conv_id, "We go to " + name + " at " + addr + ".")
	yield from bot.coro_send_message(event.conv.id_, "Find it here: " + link , image_id=image_id)
	return place["geometry"]["location"]

def whereto(bot, event, *args):
	if event.user.is_self:
		return

	if len(args) == 0:
		yield from bot.coro_send_message(event.conv_id, "I duno what you want to do ¯\\\_(ツ)_/¯")
		return

	what = args[0].lower().strip()
	if what == "drunk":
		location = yield from query(bot, event, 'bar', args[-1:])
		yield from maybedrink(bot, event, location)
	elif what == "food":
		yield from query(bot, event, 'restaurant', args[-1:])
	elif what == "junkfood":
		yield from query(bot, event, 'meal_takeaway', args[-1:])
	elif what == "party":
		location = yield from query(bot, event, 'night_club', args[-1:])
		yield from maybedrink(bot, event, location)
	else:
		yield from bot.coro_send_message(event.conv_id, "I don't know where to " + what + "\nI only know where to drunk or food")
