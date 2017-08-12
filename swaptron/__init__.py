import asyncio, aiohttp, re, os, io, tempfile, shutil
import plugins, logging

logger = logging.getLogger(__name__)


class AlexIsANoobException(Exception):
    pass

try:
    from .faceswap import *
    from wand.image import Image
    import PIL.Image
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

def save_gif(infile, output):
    im = PIL.Image.open(infile)
    i = 0
    mypalette = im.getpalette()

    try:
        while 1:
            im.putpalette(mypalette)
            new_im = PIL.Image.new("RGBA", im.size)
            new_im.paste(im)
            new_im.save(output.format(str(i)))

            i += 1
            im.seek(im.tell() + 1)
    except EOFError:
        pass # end of sequence

def swappimation(bot, event, image, source):
    tmpdir = tempfile.mkdtemp()
    frame_delays = []

    image.save(filename=tmpdir + "/tmp.gif")
    save_gif(tmpdir + "/tmp.gif", tmpdir + "/i-{0}.png")

    for cur, frame in enumerate(image.sequence):
        frame_delays.append(frame.delay)

        in_file = tmpdir + "/i-" + str(cur) + ".png"
        out_file = tmpdir + "/o-" + str(cur) + ".png"
        try:
            swap_image(in_file, current_dir+"/pics/"+source+".jpg", out_file)
        except Exception as e:
            logger.warn(str(e))


    with Image() as out_img:
        for cur, delay in enumerate(frame_delays):
            try:
                with Image(filename=tmpdir + "/o-" + str(cur) + ".png") as img:
                    out_img.sequence.append(img)
            except:
                with Image(filename=tmpdir + "/i-" + str(cur) + ".png") as img:
                    out_img.sequence.append(img)

            with out_img.sequence[cur] as frame:
                frame.delay = delay

        out_img.format = 'GIF'
        out_img.type = 'optimize'
        image_id = yield from bot._client.upload_image(io.BytesIO(out_img.make_blob(format="gif")), filename=source+'.gif')
        yield from bot.coro_send_message(event.conv.id_, None, image_id=image_id)

    shutil.rmtree(tmpdir)


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
