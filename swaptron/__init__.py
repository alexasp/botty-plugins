import asyncio, aiohttp, re, os, io, tempfile, shutil
import plugins, logging
from multiprocessing import Pool

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
self_flag = False

def _initialise(bot):
    plugins.register_handler(store_image, type="message", priority=1)
    plugins.register_handler(store_image_bot, type="allmessages", priority=1)
    plugins.register_user_command(["dannify", "danify", "andify", "alify", "allify", "robbify", "robify", "jensify"])

def store_image_bot(bot, event, command):
    global self_flag

    if event.user.is_self:
        if not self_flag:
            store_image(bot, event, command)
        self_flag = False

def store_image(bot, event, command):
    global image_posted_url
    if "lh3.googleusercontent.com" in event.text:
        image_posted_url = event.text

def save_gif(infile, output):
    def analyseImage(infile):
        im = PIL.Image.open(infile)
        results = {
            'size': im.size,
            'mode': 'full',
        }
        try:
            while True:
                if im.tile:
                    tile = im.tile[0]
                    update_region = tile[1]
                    update_region_dimensions = update_region[2:]
                    if update_region_dimensions != im.size:
                        results['mode'] = 'partial'
                        break
                im.seek(im.tell() + 1)
        except EOFError:
            pass
        return results

    def processImage(infile):
        mode = analyseImage(infile)['mode']
        im = PIL.Image.open(infile)
        i = 0
        p = im.getpalette()
        last_frame = im.convert('RGBA')

        try:
            while True:
                if not im.getpalette():
                    im.putpalette(p)

                new_frame = PIL.Image.new('RGBA', im.size)

                if mode == 'partial':
                    new_frame.paste(last_frame)

                new_frame.paste(im, (0,0), im.convert('RGBA'))
                yield new_frame

                i += 1
                last_frame = new_frame
                im.seek(im.tell() + 1)
        except EOFError:
            pass

    for i, frame in enumerate(processImage(infile)):
        frame.save(output.format(str(i)))

#def swap_process(in_file, out_file, source_file):
def swap_process(args):
    try:
        #swap_image(in_file, source_file, out_file)
        swap_image(args[0], args[2], args[1])
    except Exception as e:
        pass
    return args

def run_swap(parallell, pmap):
    if parallell:
        thread_pool = Pool(8)
        logger.info('pool spawnd')
        #chunksize = len(p_map)//4 if len(p_map) >= 4 else 1
        #thread_pool.map(swap_process, p_map, chunksize=chunksize)
        thread_pool.map(swap_process, pmap)

        # Make sure python cleans up FFS
        thread_pool.terminate()
        thread_pool.join()
    else:
        for arg in pmap:
            swap_process(arg)

def swappimation(bot, event, image, source):
    tmpdir = tempfile.mkdtemp()
    frame_delays = []

    image.save(filename=tmpdir + "/tmp.gif")
    save_gif(tmpdir + "/tmp.gif", tmpdir + "/i-{0}.png")

    p_map = []
    for cur in range(len(image.sequence)):
        with image.sequence[cur] as frame:
            frame_delays.append(frame.delay)
        p_map.append((
            tmpdir + "/i-" + str(cur) + ".png",
            tmpdir + "/o-" + str(cur) + ".png",
            current_dir+"/pics/"+source+".jpg"
        ))

    run_swap(False, p_map)

    with Image() as out_img:
        for cur, delay in enumerate(frame_delays):
            try:
                with Image(filename=tmpdir + "/o-" + str(cur) + ".png") as img:
                    out_img.sequence.append(img)
            except:
                with Image(filename=tmpdir + "/i-" + str(cur) + ".png") as img:
                    out_img.sequence.append(img)

        for cur in range(len(out_img.sequence)):
            with out_img.sequence[cur] as frame:
                frame.delay = delay

        out_img.format = 'GIF'
        out_img.type = 'optimize'
        blob = out_img.make_blob(format="gif")
        image_id = yield from bot._client.upload_image(io.BytesIO(blob), filename=source+'.gif')
        yield from bot.coro_send_message(event.conv.id_, None, image_id=image_id)

    shutil.rmtree(tmpdir)


def swappify(bot, event, source):
    global image_posted_url, self_flag
    if image_posted_url is None:
        yield from bot.coro_send_message(event.conv_id, "No image has been posted to dannify")
        return

    r = yield from aiohttp.request('get', image_posted_url)
    raw = yield from r.read()

    with Image(blob=raw) as img:
        if img.format == 'GIF' or img.animation:
            self_flag = True
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
    self_flag = True
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
