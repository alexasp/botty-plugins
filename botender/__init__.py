import asyncio, aiohttp, re, os
import plugins
import logging
import random
import io

logger = logging.getLogger(__name__)

api_key = 'f57530d036064c2b851a37fe6e6ae4fa'
url = 'http://addb.absolutdrinks.com/drinks/alcoholic/rating/gt50/withtype/'

known_types = [
    'brandy', 'gin', 'rum', 'tequila', 'vodka', 'whisky'
]

def _initialise(bot):
    plugins.register_user_command(["mixme"])

def get_image(drink_id):
    url = 'http://assets.absolutdrinks.com/drinks/300x400/' + drink_id + '.png'
    filename = os.path.basename(url)
    r = yield from aiohttp.request('get', url)
    raw = yield from r.read()
    return io.BytesIO(raw), filename

def mixme(bot, event, *args):
    if event.user.is_self:
        return

    ingredient = None
    if len(args) == 0:
        ingredient = known_types[random.randint(0,len(known_types)-1)]
    else:
        ingredient = args[0].lower()
        if ingredient not in known_types:
            yield from bot.coro_send_message(event.conv_id, "I duno how to mix with " + ingredient)
            return

    r = yield from aiohttp.request("get", url + ingredient + '/?apiKey=' + api_key)
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
