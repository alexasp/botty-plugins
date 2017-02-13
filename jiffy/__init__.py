import asyncio, aiohttp, re, os
import plugins
import logging
import random
import io

logger = logging.getLogger(__name__)
api_key = 'dc6zaTOxFJmzC'

def _initialise(bot):
    #plugins.register_handler(_handle_action)
    plugins.register_user_command(["giphy"])

def giphy(bot, event, *args):
    if event.user.is_self:
        return

    if len(args) >= 1:
        giphy_keywords = '+'.join(list(args))

    search_term = giphy_keywords.lower()

    r = yield from aiohttp.request('get', 'http://api.giphy.com/v1/gifs/search?q='+ search_term +'&limit=25&api_key=dc6zaTOxFJmzC')
    r_json = yield from r.json()
    
    if len(r_json['data']) == 0:
        yield from bot.coro_send_message(event.conv_id, 'No hits.')
        return

    image_link = r_json['data'][random.randint(0,len(r_json['data'])-1)]['images']['original']['url']
    
    filename = os.path.basename(image_link)
    r = yield from aiohttp.request('get', image_link)
    raw = yield from r.read()
    image_data = io.BytesIO(raw)
    image_id = yield from bot._client.upload_image(image_data, filename=filename)
    yield from bot.coro_send_message(event.conv.id_, None, image_id=image_id)
