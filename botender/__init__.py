import asyncio, aiohttp, re, os
import plugins
import logging
import random
import io

logger = logging.getLogger(__name__)

api_key = 'f57530d036064c2b851a37fe6e6ae4fa'
url = 'http://addb.absolutdrinks.com/'

known_types = [
    'brandy', 'gin', 'rum', 'tequila', 'vodka', 'whisky', 'champagne'
]

known_tastes = [
    'berry', 'bitter', 'fresh', 'fruity', 'sour', 'spicy', 'sweet'
]

def _initialise(bot):
	plugins.register_user_command(["mixme", "illhaveone"])
	bot.register_shared("mixme.here", get_one_here)

def get_image(drink_id):
    url = 'http://assets.absolutdrinks.com/drinks/300x400/' + drink_id + '.png'
    filename = os.path.basename(url)
    r = yield from aiohttp.request('get', url)
    raw = yield from r.read()
    return io.BytesIO(raw), filename

def get_one_here(bot, location):
	logger.info(location)
	r = yield from aiohttp.request("get", url + 'illhaveones/near/' + location + ',50/?apiKey=' + api_key)				
	r_json = yield from r.json()
	if len(r_json["result"]) == 0:
		return False, '', None
	
	drink = r_json["result"][random.randint(0, len(r_json["result"])-1)]
	image_data, filename = yield from get_image(drink["drink"]["id"])
	image_id = yield from bot._client.upload_image(image_data, filename=filename)
	return True, drink["drink"]["text"], image_id
	
def illhaveone(bot, event, *args):
	if event.user.is_self:
		return
	
	if len(args) == 0 or args[0].lower() == 'in':
		where = 'oslo'
		if len(args) > 1:
			where = args[1]
		
		r = yield from aiohttp.request("get", url + 'illhaveones/incity/' + where + '/?apiKey=' + api_key)				
		r_json = yield from r.json()
		if len(r_json["result"]) == 0:
			yield from bot.coro_send_message(event.conv_id, "sry, I duno what u can have in " + where)
			return
		
		drink = r_json["result"][random.randint(0, len(r_json["result"])-1)]
		image_data, filename = yield from get_image(drink["drink"]["id"])
		image_id = yield from bot._client.upload_image(image_data, filename=filename)
		yield from bot.coro_send_message(event.conv_id, "You can have a <b>" + drink["drink"]["text"] + "</b>", image_id=image_id)
		try:
			success, name, loc_url, image_id = yield from bot.call_shared("where.placeat", bot, str(drink["latitude"]) + "," + str(drink["longitude"]), 'bar')
			if success:
				yield from bot.coro_send_message(event.conv_id, "At " + name + "(" + loc_url + ")", image_id=image_id)
		except Exception as e:
			yield from bot.coro_send_message(event.conv_id, "I depend on 'whereto' to werk, pliz tell Alex to load it")
			logger.info (e)
	elif args[0].lower() == 'here':
		try:
			success, location = bot.call_shared("where.ami", bot, event.user)
			if success:				
				success, name, image_id = yield from get_one_here(bot, location)
				if success:
					yield from bot.coro_send_message(event.conv_id, "You can have a <b>" + name + "</b>", image_id=image_id)
				else:
					yield from bot.coro_send_message(event.conv_id, "sry, I duno what u can have here")
			else:
				yield from bot.coro_send_message(event.conv_id, "I duno where you are, pliz share location")
		except:
			yield from bot.coro_send_message(event.conv_id, "I depend on 'whereto' to werk, pliz tell Alex to load it")

	
def mixme(bot, event, *args):
	if event.user.is_self:
		return

	ingredient = None
	taste = None
	term = []
	if len(args) == 0:
		ingredient = known_types[random.randint(0,len(known_types)-1)]
	else:
		for arg in args:
			if arg.lower() in known_types and ingredient is None:
				ingredient = arg.lower()
			elif arg.lower() in known_tastes and taste is None:
				taste = arg.lower()
			else:
				term.append(arg)

	url_append = ''
	if ingredient is not None or taste is not None:
		url_append = 'drinks/alcoholic/rating/gt50/'
		if ingredient is not None:
			url_append += 'withtype/' + ingredient + '/'
		if taste is not None:
			url_append += 'tasting/' + taste + '/'
	else:
		url_append = 'quickSearch/drinks/' + "+".join(term)
		
	r = yield from aiohttp.request("get", url + url_append + '/?apiKey=' + api_key)	
	r_json = yield from r.json()
	if r_json["totalResult"] == 0:
		yield from bot.coro_send_message(event.conv_id, "I duno how to mix with " + ingredient)
		return

	drink = r_json["result"][random.randint(0, len(r_json["result"])-1)]

	result = "<b>" + drink["name"] + "</b>\n"
	result += drink["descriptionPlain"] +  " <i>Served in a " + drink["servedIn"]["text"].lower() + "</i> \n"
	ingedirents = "\n<b>Ingredients:</b>\n"
	for ing in drink["ingredients"]:
		ingedirents += '- ' + ing["textPlain"] + "\n"
	result += ingedirents

	image_data, filename = yield from get_image(drink["id"])
	image_id = yield from bot._client.upload_image(image_data, filename=filename)
	yield from bot.coro_send_message(event.conv_id, result, image_id=image_id)
