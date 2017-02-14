import asyncio, aiohttp, re, os
import plugins
import logging
import random
import io

logger = logging.getLogger(__name__)

def _initialise(bot):
    plugins.register_user_command(["whatis"])

def whatis(bot, event, *args):
    if event.user.is_self:
        return

    search_term = "+".join(args).lower()

    r = yield from aiohttp.request('get', 'https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&titles='+search_term+'&formatversion=2&exsentences=1&explaintext=1&exsectionformat=plain')
    r_json = yield from r.json()

    if len(r_json['query']) == 0:
        yield from bot.coro_send_message(event.conv_id, 'No hits.')
        return

    extract = r_json['query']['pages'][random.randint(0,len(r_json['query']['pages'])-1)]['extract']
    yield from bot.coro_send_message(event.conv_id, extract)
