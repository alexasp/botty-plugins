import asyncio, aiohttp, re, os
import plugins
import logging
import random
import io

logger = logging.getLogger(__name__)

headers={
  "X-Mashape-Key": "CZrByDIfctmshUZlKmwtVsg64yNSp14UJ6jjsnCSwRfXEPI0If",
  "accept": "application/hal+json"
}

ask_donald_url = "https://matchilling-tronald-dump-v1.p.mashape.com/search/quote?query="
random_donald_url = "https://matchilling-tronald-dump-v1.p.mashape.com/random/quote"

def _initialise(bot):
    plugins.register_user_command(["askdonald"])

def askdonald(bot, event, *args):
    if event.user.is_self:
        return

    if len(args) == 0:
        r = yield from aiohttp.request("get", random_donald_url, headers=headers)
        quote = yield from r.json()
        yield from bot.coro_send_message(event.conv_id, quote["value"])
    else:
        query = "+".join(args)
        r = yield from aiohttp.request("get", ask_donald_url + query, headers=headers)
        r_json = yield from r.json()
        if r_json['count'] > 0:
            quote = r_json["_embedded"]["quotes"][random.randint(0, r_json['count']-1)]
            yield from bot.coro_send_message(event.conv_id, quote["value"])
        else:
            r = yield from aiohttp.request("get", random_donald_url, headers=headers)
            quote = yield from r.json()
            yield from bot.coro_send_message(event.conv_id, quote["value"])
