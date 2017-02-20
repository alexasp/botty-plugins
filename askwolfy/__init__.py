import asyncio, aiohttp, re, os
import plugins
import logging
import random
import io
from urllib import parse

logger = logging.getLogger(__name__)
app_id = 'LQUEWT-YXJHERYLJG'

def _initialise(bot):
    plugins.register_user_command(["ask"])

def ask(bot, event, *args):
    if event.user.is_self:
        return

    if len(args) == 0:
        yield from bot.coro_send_message(event.conv_id, "You have to ask something dummy")
        return

    question = parse.quote_plus(" ".join(args))

    url = 'https://www.wolframalpha.com/queryrecognizer/query.jsp?mode=Default&i=' + question + '&output=JSON&appid=' + 'DEMO'#app_id
    r = yield from aiohttp.request('get', url)
    test = yield from r.json()
    if test["query"][0]["accepted"] is False:
        yield from bot.coro_send_message(event.conv_id, "I don't understand your question ¯\\\_(ツ)_/¯")

    url = 'https://api.wolframalpha.com/v1/result?i=' + question + '&appid=' + app_id
    logger.info(url)
    r = yield from aiohttp.request('get', url)
    answer = yield from r.text()
    yield from bot.coro_send_message(event.conv_id, answer)
