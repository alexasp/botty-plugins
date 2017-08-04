import asyncio, aiohttp, re, os, io, tempfile
import plugins, logging

logger = logging.getLogger(__name__)


class AlexIsANoobException(Exception):
    pass

try:
    from .faceswap import *
except:
    raise AlexIsANoobException("Alex doesn't understand how to install software")

image_posted_url = None

def _initialise(bot):
    plugins.register_handler(store_image, type="message", priority=1)
    #plugins.register_handler(store_image_bot, type="sending", priority=1)
    plugins.register_user_command(["dannify", "andify", "alify", "robbify", "jensify"])

def store_image(bot, event, command):
    global image_posted_url
    if "lh3.googleusercontent.com" in event.text:
        image_posted_url = event.text

#def store_image_bot(bot, broadcast_list, context):
#    global image_posted_url
#    segments = broadcast_list[0][1]
#    for segment in segments:
#        if "lh3.googleusercontent.com" in segment.text:
#            image_posted_url = event.text

def swappify(bot, event, source):
    global image_posted_url
    if image_posted_url is None:
        yield from bot.coro_send_message(event.conv_id, "No image has been posted to dannify")
        return

    logger.info(image_posted_url)
    r = yield from aiohttp.request('get', image_posted_url)
    raw = yield from r.read()
    tmp = tempfile.NamedTemporaryFile()
    tmp.write(raw)

    out_tmp = tempfile.gettempdir() + source + "_output.jpg"
    try:
        swap_image(tmp.name, "./plugins/botty-plugins/swaptron/pics/"+source+".jpg", out_tmp)
    except:
        yield from bot.coro_send_message(event.conv_id, "Failed to swap")
        return

    image_data = io.FileIO(out_tmp, 'r')
    image_id = yield from bot._client.upload_image(image_data, filename=out_tmp)
    yield from bot.coro_send_message(event.conv.id_, None, image_id=image_id)
    os.remove(out_tmp)

def dannify(bot, event, *args):
    yield from swappify(bot, event, "danny")
def andify(bot, event, *args):
    yield from swappify(bot, event, "andre")
def alify(bot, event, *args):
    yield from swappify(bot, event, "alex")
def robbify(bot, event, *args):
    yield from swappify(bot, event, "robin")
def jensify(bot, event, *args):
    yield from swappify(bot, event, "jens")
