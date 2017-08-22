import plugins, logging
import asyncio, aiohttp, io, os, re, tempfile

class AlexIsAHugeNoobException(Exception):
    pass

try:
    from wand.image import Image
    from wand.font import Font
    from wand.color import Color
    from wand.drawing import Drawing
except:
    raise AlexIsANoobException("Alex doesn't understand how to install software")

logger = logging.getLogger(__name__)

image_posted_url = None
current_dir = os.path.dirname(os.path.realpath(__file__))
self_flag = False

def _initialise(bot):
    plugins.register_handler(store_image, type="message", priority=1)
    plugins.register_handler(store_image_bot, type="allmessages", priority=1)
    plugins.register_user_command(["andymemer", "dannymemer", "allymemer", "robbymemer", "jensymemer", "memit", "listmems"])

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

def getmems(path):
    return [f.split('.')[0] for f in os.listdir(current_dir+path) if f.endswith('.jpg')]

def listmems(bot, event, *args):
    mems = ["danny", "ally", "robby", "jensy", "andy"]
    list_mems = []
    if len(args) == 0:
        list_mems = mems
    else:
        for arg in args:
            if arg in mems:
                list_mems.append(arg)
            else:
                yield from bot.coro_send_message(event.conv_id, "Don't know mem: <b>" + arg + "</b>")
    for mem in list_mems:
        yield from bot.coro_send_message(event.conv_id, mem + "mems: <b>" + "</b> <b>".join(getmems('/memes/'+mem+'/')) + "</b>")

def dannymemer(bot, event, *args):
    yield from memer(bot, event, "danny", getmems('/memes/danny/'), *args)

def allymemer(bot, event, *args):
    yield from memer(bot, event, "ally", getmems('/memes/ally/'), *args)

def robbymemer(bot, event, *args):
    yield from memer(bot, event, "robby", getmems('/memes/robby/'), *args)

def jensymemer(bot, event, *args):
    yield from memer(bot, event, "jensy", getmems('/memes/jensy/'), *args)

def andymemer(bot, event, *args):
    yield from memer(bot, event, "andy", getmems('/memes/andy/'), *args)

def memit(bot, event, *args):
    global image_posted_url

    if image_posted_url is None:
        yield from bot.coro_send_message(event.conv_id, "No image to meme")
        return

    if len(args) < 2:
        yield from bot.coro_send_message(event.conv_id, "I can't make meme with this! try")
        yield from bot.coro_send_message(event.conv_id, "/bot memit \"<top text>\" \"<bottom text>\"")
        return

    r = yield from aiohttp.request('get', image_posted_url)
    raw = yield from r.read()

    toptext = args[0].replace('"', '').upper()
    bottomtext = args[1].replace('"', '').upper()
    yield from make_meme(bot, event, toptext, bottomtext, base_image_blob=raw)

def memer(bot, event, name, memes, *args):
    if event.user.is_self:
        return

    if len(args) < 3:
        yield from bot.coro_send_message(event.conv_id, "I can't make "+name+"meme with this! try")
        yield from bot.coro_send_message(event.conv_id, "/bot "+name+"memer <meme> \"<top text>\" \"<bottom text>\"")
        return

    meme = args[0]
    if meme not in memes:
        yield from bot.coro_send_message(event.conv_id, "I don't know the "+name+"meme " + meme)
        yield from bot.coro_send_message(event.conv_id, "Try one of these <b>" + "</b> <b>".join(memes) + "</b>")
        return

    toptext = args[1].replace('"', '').upper()
    bottomtext = args[2].replace('"', '').upper()
    base_img = current_dir+"/memes/"+name+"/"+meme+".jpg"
    yield from make_meme(bot, event, toptext, bottomtext, base_image_path=base_img)

def make_meme(bot, event, toptext, bottomtext, base_image_path=None, base_image_blob=None):
    global self_flag
    with Image(filename=base_image_path, blob=base_image_blob) as i:

        with Drawing() as draw:
            draw.stroke_color = Color('black')
            draw.fill_color = Color('white')
            draw.stroke_width = 3
            draw.text_alignment = 'center'
            draw.font = current_dir+'/impactreg.ttf'
            draw.font_size = 112
            draw.gravity = 'center'
            draw.text_antialias = True

            max_width = i.size[0]
            max_text_height = int(i.size[1]*0.3)
            def splitText(text):
                metrics = draw.get_font_metrics(i, text, multiline=False)
                if(metrics.text_width > max_width):
                    tmp = text.split(' ')
                    if len(tmp) == 1: return splitText(tmp[0][::2]) + '...\n' + splitText(tmp[0][1::2])
                    return splitText(' '.join(tmp[:len(tmp)//2])) + '\n' + splitText(' '.join(tmp[len(tmp)//2:]))
                return text

            def scaleText(text):
                tmp = splitText(text)
                metrics = draw.get_font_metrics(i, tmp, multiline=True)
                if (metrics.text_height > max_text_height or metrics.text_width > max_width) and draw.font_size > 40:
                    draw.font_size = draw.font_size - 20
                    return scaleText(text)
                else:
                    return tmp

            draw.font_size = 140
            tmp_top = scaleText(toptext)
            metrics = draw.get_font_metrics(i, tmp_top, multiline=True)
            draw.text(max_width//2, 10 + int(metrics.character_height), tmp_top)

            draw.font_size = 140
            tmp_bottom = scaleText(bottomtext)
            metrics = draw.get_font_metrics(i, tmp_bottom, multiline=True)
            draw.text(max_width//2, (i.size[1]-20) + int(metrics.character_height) - int(metrics.text_height), tmp_bottom)

            draw(i)
            self_flag = True
            image_id = yield from bot._client.upload_image(io.BytesIO(i.make_blob(format=i.format)), filename='meme.' + i.format)
            yield from bot.coro_send_message(event.conv.id_, None, image_id=image_id)
