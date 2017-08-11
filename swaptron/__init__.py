import asyncio, aiohttp, re, os, io, tempfile
import plugins, logging

logger = logging.getLogger(__name__)


class AlexIsANoobException(Exception):
    pass

try:
    from .faceswap import *
    from wand.image import Image
except:
    raise AlexIsANoobException("Alex doesn't understand how to install software")

image_posted_url = None
current_dir = os.path.dirname(os.path.realpath(__file__))

def _initialise(bot):
    plugins.register_handler(store_image, type="message", priority=1)
    #plugins.register_handler(store_image_bot, type="sending", priority=1)
    plugins.register_user_command(["dannify", "danify", "andify", "alify", "allify", "robbify", "robify", "jensify"])

def store_image(bot, event, command):
    global image_posted_url
    if "lh3.googleusercontent.com" in event.text:
        image_posted_url = event.text

def swappimation(bot, event, image, source):
    yield from bot.coro_send_message(event.conv.id_, "IT IS A GIF!")

def swappify(bot, event, source):
    global image_posted_url
    if image_posted_url is None:
        yield from bot.coro_send_message(event.conv_id, "No image has been posted to dannify")
        return

    r = yield from aiohttp.request('get', image_posted_url)
    raw = yield from r.read()

    with Image(blob=raw) as img:
        if img.format == 'GIF' or img.animation:
            yield from swappimation(bot, event, img, source)
            return

    tmp = tempfile.NamedTemporaryFile()
    tmp.write(raw)

    out_tmp = tempfile.gettempdir() + '/' + source + next(tempfile._get_candidate_names()) + ".jpg"
    try:
        swap_image(tmp.name, current_dir+"/pics/"+source+".jpg", out_tmp)
    except Exception as e:
        logger.warn(str(e))
        yield from bot.coro_send_message(event.conv_id, 'swap failed: ' + str(e))
        return

    image_data = io.FileIO(out_tmp, 'r')
    image_id = yield from bot._client.upload_image(image_data, filename=out_tmp)
    yield from bot.coro_send_message(event.conv.id_, None, image_id=image_id)
    os.remove(out_tmp)

def dannify(bot, event, *args):
    yield from swappify(bot, event, "danny")
def danify(bot, event, *args):
    yield from dannify(bot, event, *args)

def andify(bot, event, *args):
    yield from swappify(bot, event, "andre")
    
def alify(bot, event, *args):
    yield from swappify(bot, event, "alex")
def allify(bot, event, *args):
    yield from alify(bot, event, *args)

def robbify(bot, event, *args):
    yield from swappify(bot, event, "robin")
def robify(bot, event, *args):
    yield from robbify(bot, event, *args)

def jensify(bot, event, *args):
    yield from swappify(bot, event, "jens")
