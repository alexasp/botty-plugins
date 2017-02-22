import asyncio, aiohttp
import plugins
import logging
import time, random

url = "http://harmannenfaltned.no/api"

logger = logging.getLogger(__name__)

def _initialise(bot):
	plugins.register_handler(on_message, type="message", priority=5)
	plugins.register_user_command(["harmannenfalt"])

def on_message(bot, event, command):
	if "har mannen falt?" == event.text.lower().strip():
		yield from harmannenfalt(bot, event, "")

def harmannenfalt(bot, event, *args):
	if event.user.is_self:
		return

	r = yield from aiohttp.request("get", url)
	data = yield from r.json()
	falt = '<b>Ja</b>' if data['falt_ned'] else '<b>Nei</b>'
	
	if falt == '<b>Nei</b>' and random.randint(1, 6) == 2:
		yield from bot.coro_send_message(event.conv_id, '<b>Ja</b>')
		yield from asyncio.sleep(5.0)
		yield from bot.coro_send_message(event.conv_id, 'Lol tulla.')
		yield from bot.coro_send_message(event.conv_id, falt)
	else:
		yield from bot.coro_send_message(event.conv_id, falt)