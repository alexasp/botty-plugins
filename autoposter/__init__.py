import plugins, logging
import asyncio, aiohttp, io, os, re
logger = logging.getLogger(__name__)

# Hangout supported extensions
extensions = ['.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff']

def _initialise(bot):
	plugins.register_handler(on_message, type="message", priority=5)

def on_message(bot, event, command):
    message = event.text

    if (message.find('http://') is not -1 or message.find('https://') is not -1 or message.find('www') is not -1) is False:
        return
    if message.find("lh3.googleusercontent.com") is not -1:
        return

    index = -1
    for ext in extensions:
        index = message.lower().rfind(ext)
        if index is not -1: end = index+len(ext)+1; break

    if index is not -1:
        start = message.rfind(' ', 0, index)
        if start is -1: start = 0
        yield from handle_direct_link(bot, event, message[start:end].strip())

    else:
        index = message.lower().rfind("imgur.com")
        if index is not -1:
            start = message.rfind(' ', 0, index)
            if start is -1: start = 0
            end = message.find(' ', index)
            if end is -1: end = None
            yield from handle_imgur_link(bot, event, message[start:end].strip())


def handle_imgur_link(bot, event, url):
    client_id = 'b144351ffb05838'
    headers = {'Authorization': 'Client-ID ' + client_id, 'Accept': 'application/json'}


    match = re.findall(r"(?<=gallery\/)\w+", url)
    if len(match) is not 0:
        imgur_url = 'https://api.imgur.com/3/gallery/album/' + match[0]

        r = yield from aiohttp.request('get', imgur_url, headers=headers)
        r_json = yield from r.text()

        r_json = yield from r.json()

        if r_json["success"]:
            if len(r_json["data"]["images"]) > 0:
                if r_json["data"]["images"][0]["nsfw"]:
                    yield from bot.coro_send_message(event.conv.id_, "This image is NSFW!")
                else:
                    yield from handle_direct_link(bot, event, r_json["data"]["images"][0]["link"])
        return

    match = re.findall(r"(?<=\.com\/)\w+", url)
    if len(match) is not 0:
        imgur_url = 'https://api.imgur.com/3/image/' + match[0]

        r = yield from aiohttp.request('get', imgur_url, headers=headers)
        r_json = yield from r.json()

        if r_json["success"]:
            if r_json["data"]["nsfw"]:
                yield from bot.coro_send_message(event.conv.id_, "This image is NSFW!")
            else:
                yield from handle_direct_link(bot, event, r_json["data"]["link"])
        return

def handle_direct_link(bot, event, url):
    try:
        if url.find('http') is -1:
            url = "http://" + url
        filename = os.path.basename(url)
        r = yield from aiohttp.request('get', url)
        raw = yield from r.read()
        image_data = io.BytesIO(raw)
        image_id = yield from bot._client.upload_image(image_data, filename=filename)
        yield from bot.coro_send_message(event.conv.id_, None, image_id=image_id)
    except:
        pass
