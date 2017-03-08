import asyncio, aiohttp, re, os
import plugins
import logging
import random
import io

logger = logging.getLogger(__name__)
api_key = 'dc6zaTOxFJmzC'

# Set of banned users
banned_users = set()

#log last message by user
last_message = {}

def _initialise(bot):
    plugins.register_handler(jiffme, type="message", priority=5)
    plugins.register_user_command(["giphy", "jiffs", "jifflate"])
    plugins.register_admin_command(["giphyban", "giphyunban"])

def jiffme(bot, event, command):
    text_lower = event.text.lower()
    if "#jiffme" in text_lower:
        args = text_lower.split(" ")
        args.remove("#jiffme")
        if len(args) > 0:
            yield from giphy(bot, event, args[random.randint(0,len(args)-1)])
    elif "#jiffit" in text_lower:
        args = text_lower.split(" ")
        args.remove("#jiffit")
        if len(args) > 0:
            yield from jifflate(bot, event, *args)
    else:
        for key, value in last_message.items():
            if "#jiff" + key.lower() in text_lower:
                tmp = re.sub(r"\#jiff\w*", "", value)
                args = value.split(" ")
                if len(value) > 0:
                    yield from jifflate(bot, event, *args)
                break
        else:
            last_message[event.user.first_name] = text_lower
            user_nick = bot.memory.get_suboption("user_data", event.user.id_.chat_id, "nickname")
            if user_nick:
                last_message[user_nick] = text_lower

def find_user(bot, search):
    all_known_users = {}
    for chat_id in bot.memory["user_data"]:
        all_known_users[chat_id] = bot.get_hangups_user(chat_id)

    search_lower = search.strip().lower()
    for u in sorted(all_known_users.values(), key=lambda x: x.full_name.split()[-1]):
        if( search_lower in u.full_name.lower() ):
            return u
    return None

def giphyban(bot, event, *args):
    if event.user.is_self:
        return
    u = find_user(bot, " ".join(args))
    if(u is not None):
        banned_users.add(u.id_.chat_id)
        yield from bot.coro_send_message(event.conv, "Banned the shit out of " + u.full_name)
    else:
        yield from bot.coro_send_message(event.conv, "Failed to find user" + " ".join(args))

def giphyunban(bot, event, *args):
    if event.user.is_self:
        return
    u = find_user(bot, " ".join(args))
    if(u is not None):
        banned_users.remove(u.id_.chat_id)
        yield from bot.coro_send_message(event.conv.id_, "Removing the ban from user " + u.full_name + " so hard")
    else:
        yield from bot.coro_send_message(event.conv.id_, "Failed to find user" + " ".join(args))


def giphy_search(bot, event, term):

	r = yield from aiohttp.request('get', 'http://api.giphy.com/v1/gifs/search?q='+ term +'&limit=25&api_key=dc6zaTOxFJmzC')
	r_json = yield from r.json()

	if 'data' in r_json and len(r_json['data']) == 0:
		yield from bot.coro_send_message(event.conv_id, 'No hits.')
		return

	image_link = r_json['data'][random.randint(0,len(r_json['data'])-1)]['images']['original']['url']

	filename = os.path.basename(image_link)
	r = yield from aiohttp.request('get', image_link)
	raw = yield from r.read()
	image_data = io.BytesIO(raw)
	image_id = yield from bot._client.upload_image(image_data, filename=filename)
	yield from bot.coro_send_message(event.conv.id_, None, image_id=image_id)

def giphy_translate(bot, event, term):
	r = yield from aiohttp.request('get', 'http://api.giphy.com/v1/gifs/translate?s='+ term +'&api_key=dc6zaTOxFJmzC')
	r_json = yield from r.json()

	if 'data' in r_json and len(r_json['data']) == 0:
		yield from bot.coro_send_message(event.conv_id, 'No hits.')
		return

	image_link = r_json['data']['images']['original']['url']

	filename = os.path.basename(image_link)
	r = yield from aiohttp.request('get', image_link)
	raw = yield from r.read()
	image_data = io.BytesIO(raw)
	image_id = yield from bot._client.upload_image(image_data, filename=filename)
	yield from bot.coro_send_message(event.conv.id_, None, image_id=image_id)

def jifflate(bot, event, *args):
	if event.user.is_self:
		return

	if event.user.id_.chat_id in banned_users:
		yield from bot.coro_send_message(event.conv.id_, "lol u r banned")
		return

	if len(args) >= 1:
		giphy_keywords = '+'.join(list(args))

	search_term = giphy_keywords.lower()
	yield from giphy_translate(bot, event, search_term)

def jiffs(bot, event, *args):
	yield from giphy(bot, event, *args)

def giphy(bot, event, *args):
	if event.user.is_self:
		return

	if event.user.id_.chat_id in banned_users:
		yield from bot.coro_send_message(event.conv.id_, "lol u r banned")
		return

	if len(args) >= 1:
		giphy_keywords = '+'.join(list(args))

	search_term = giphy_keywords.lower()
	yield from giphy_search(bot, event, search_term)
