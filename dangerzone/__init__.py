import asyncio, aiohttp, re, os
import plugins
import logging
import random
import io

logger = logging.getLogger(__name__)
client_id = 'b144351ffb05838'
url = 'https://api.imgur.com/3/gallery/r/FiftyFifty/time/'
img_url = 'https://api.imgur.com/3/gallery/r/FiftyFifty/'
headers = {'Authorization': 'Client-ID ' + client_id, 'Accept': 'application/json'}
balls_being_checked = {}

approved_convs = set()

def _initialise(bot):
    plugins.register_handler(on_message, type="message", priority=5)
    plugins.register_user_command(["checkmyballs"])
    plugins.register_admin_command(["takeustothedangerzone", "getusoutofthedangerzone"])

def takeustothedangerzone(bot, event, *args):
    if event.user.is_self:
        return
    yield from bot.coro_send_message(event.conv_id, "All abord the highway to the danger zone")
    approved_convs.add(event.conv_id)

def getusoutofthedangerzone(bot, event, *args):
    if event.user.is_self:
        return
    yield from bot.coro_send_message(event.conv_id, "Getting the FUCK out of the danger zone")
    approved_convs.remove(event.conv_id)

def on_message(bot, event, command):
    if event.user.is_self:
        return

    global balls_being_checked
    user_id = event.user.id_.chat_id

    if user_id not in balls_being_checked:
        return
    if balls_being_checked[user_id][0] is False:
        return

    if "i lack the balls" == event.text.lower().strip():
        balls_being_checked[user_id] = (False, None)
        yield from bot.coro_send_message(event.conv_id, event.user.full_name + " lacks the balls")
    elif "i have the balls" == event.text.lower().strip():
        link = balls_being_checked[user_id][1]
        logger.info(link)

        if event.conv_id not in approved_convs:
            yield from bot.coro_send_message(event.conv_id, "Alex doesn't want to take us on to the highway to the danger zone")
            return

        filename = os.path.basename(link)
        r = yield from aiohttp.request('get', link)
        raw = yield from r.read()
        image_data = io.BytesIO(raw)
        image_id = yield from bot._client.upload_image(image_data, filename=filename)
        yield from bot.coro_send_message(event.conv.id_, None, image_id=image_id)
        balls_being_checked[user_id] = (False, None)

def checkmyballs(bot, event, *args):
    if event.user.is_self:
        return

    if event.conv_id not in approved_convs:
        yield from bot.coro_send_message(event.conv_id, "Alex doesn't want to take us on to the highway to the danger zone")
        return

    global balls_being_checked
    user_id = event.user.id_.chat_id
    if user_id in balls_being_checked and balls_being_checked[user_id][0] is True:
        yield from bot.coro_send_message(event.conv_id, event.user.full_name + " is already getting his balls checked")
        return

    r = yield from aiohttp.request('get', url + str(random.randint(0, 50)) +'/year', headers=headers)
    r_json = yield from r.json()
    if len(r_json["data"]) == 0:
        yield from bot.coro_send_message(event.conv_id, "Failed to find image :(")
        return

    sel = r_json["data"][random.randint(0, len(r_json["data"])-1)]
    title = re.sub(r"\[.+?\]|\(.+?\)|N?SFL?W?(\/L)?", "", sel["title"])
    titles = re.split(r"\s+\|\s+|\s+or\s+|\s+\/\s+|\s+\\\s+", title)
    if len(titles) != 2:
        logger.info("Failed to parse: " + title)
        logger.info("Parsed titles: [" + "], [".join(titles) + "]")
        yield from bot.coro_send_message(event.conv_id, "I failed to parse reddit title :(")
        return

    r = yield from aiohttp.request('get', img_url + sel["id"], headers=headers)
    r_json = yield from r.json()
    link = r_json["data"]["link"]

    yield from bot.coro_send_message(event.conv_id, "<b>" + titles[0].strip() + "</b> or <b>" + titles[1].strip() + "</b>")

    balls_being_checked[user_id] = (True, link)
    yield from bot.coro_send_message(event.conv_id, "So, " + event.user.full_name +  " do you have the balls, or do you lack the balls??")
