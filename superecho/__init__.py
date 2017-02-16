import asyncio, aiohttp, re, os
import plugins
import logging
import random
import io

logger = logging.getLogger(__name__)

headers={
  "X-Mashape-Key": "CZrByDIfctmshUZlKmwtVsg64yNSp14UJ6jjsnCSwRfXEPI0If"
}

def _initialise(bot):
    plugins.register_user_command(["yodaecho", "leetecho", "yarrecho"])

def quoteit():
    url = 'https://andruxnet-random-famous-quotes.p.mashape.com/?cat=famous'
    r = yield from aiohttp.request("post", url, headers=headers)
    quote = yield from r.json()
    return quote['quote']

def echo(bot, event, url, args):
    text = ''
    if len(args) == 0:
        quote = yield from quoteit()
        text = "+".join(quote.split(" "))
    else:
        text = "+".join(args)

    r = yield from aiohttp.request("get", url + text, headers=headers)
    echo = yield from r.text()
    yield from bot.coro_send_message(event.conv_id, echo)

def yodaecho(bot, event, *args):
    if event.user.is_self:
        return
    yield from echo(bot, event, 'https://yoda.p.mashape.com/yoda?sentence=', args)

def leetecho(bot, event, *args):
    if event.user.is_self:
        return
    yield from echo(bot, event, 'https://montanaflynn-l33t-sp34k.p.mashape.com/encode?text=', args)
