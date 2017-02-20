
import asyncio, aiohttp, re, os
import plugins
import logging
import random
import io

logger = logging.getLogger(__name__)
my_bros = set()

def _initialise(bot):
    plugins.register_handler(on_message, type="message", priority=5)
    plugins.register_user_command(["bemybro"])
    plugins.register_user_command(["insult"])

def on_message(bot, event, command):
    for bro in my_bros:
        if bro.lower() in event.text.lower():
            yield from back_up(bro, bot, event, command)

def back_up(bro, bot, event, command):
    headers={
      "X-Mashape-Key": "CZrByDIfctmshUZlKmwtVsg64yNSp14UJ6jjsnCSwRfXEPI0If",
      "Content-Type": "application/x-www-form-urlencoded",
      "Accept": "application/json"
    }
    url = 'https://community-sentiment.p.mashape.com/text/'
    r = yield from aiohttp.request("post", url, headers=headers, data={
        "txt": event.text
    })
    r_json = yield from r.json()
    if r_json["result"]["sentiment"] == "Negative":
        yield from bot.coro_send_message(event.conv_id, "I am " + r_json["result"]["confidence"] + "% sure you just insulted my bro " + bro)
        yield from insult(bot, event, event.user.full_name.split(" ")[0])

def bemybro(bot, event, *args):
    if event.user.is_self:
        return

    if len(args) == 0:
        yield from bot.coro_send_message(event.conv_id, "Missing argument")
        return

    name = event.user.full_name.split(" ")[0]
    if args[0] == "start":
        yield from bot.coro_send_message(event.conv_id, name + " is now my bro")
        my_bros.add(name)
    elif args[0] == "stop":
        yield from bot.coro_send_message(event.conv_id, name + " is no longer my bro, but I still love him")
        my_bros.remove(name)

def insult(bot, event, *args):
    if event.user.is_self:
        return

    if len(args) == 0:
        yield from bot.coro_send_message(event.conv_id, "I duno who to insult")
        return

    who = " ".join(args)
    if "jens" in who.lower():
        yield from bot.coro_send_message(event.conv_id, who + " is the real guy, the best guy")
        return

    if "daniel" in event.user.full_name.lower():
        who = event.user.full_name

    url = 'http://autoinsult.datahamster.com/scripts/webinsult.server.php?xajax=generate_insult&xajaxargs[]=3'
    r = yield from aiohttp.request("get", url)
    xml = yield from r.text()
    text = re.search(r"\!\[CDATA\[You(.*?)\]\]", xml).group(1)
    yield from bot.coro_send_message(event.conv_id, who + ' is a' + text)
