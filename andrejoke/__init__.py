import plugins, logging, asyncio, aiohttp, time, random
from commands import command

logger = logging.getLogger(__name__)

url = "https://icanhazdadjoke.com/"

@command.register
def andréjoke(bot, event, *args):
    r = yield from aiohttp.request("get", url, headers={'Accept': 'application/json'})
    data = yield from r.json()
    yield from bot.coro_send_message(event.conv_id, data['joke'])
    yield from asyncio.sleep(5.0)
    yield from bot.coro_send_message(event.conv_id, '<i>hehe</i>')
