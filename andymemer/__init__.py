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


memes = ["disgust","funi","insulted","china","weird","what"]
logger = logging.getLogger(__name__)

def _initialise(bot):
    plugins.register_user_command(["andymemer"])

def andymemer(bot, event, *args):
    if event.user.is_self:
        return

    if len(args) != 3:
        yield from bot.coro_send_message(event.conv_id, "I can't make andymeme with this! try")
        yield from bot.coro_send_message(event.conv_id, "/bot andymemer <meme> \"<top text>\" \"<bottom text>\"")
        return

    meme = args[0]
    if meme not in memes:
        yield from bot.coro_send_message(event.conv_id, "I don't know the andymeme " + meme)
        yield from bot.coro_send_message(event.conv_id, "Try one of these <b>" + "</b> <b>".join(memes) + "</b>")
        return

    toptext = args[1].replace('"', '').upper()
    bottomtext = args[2].replace('"', '').upper()

    with Image(filename="./plugins/botty-plugins/andymemer/memes/"+meme+".jpg") as i:

        with Drawing() as draw:
            draw.stroke_color = Color('black')
            draw.fill_color = Color('white')
            draw.stroke_width = 5
            draw.text_alignment = 'center'
            draw.font = './plugins/botty-plugins/andymemer/impactreg.ttf'
            draw.font_size = 112
            draw.gravity = 'center'
            draw.text_antialias = True

            def splitText(text):
                metrics = draw.get_font_metrics(i, text, multiline=True)
                if(metrics.text_width > 900):
                    tmp = text.split(' ')
                    return splitText(' '.join(tmp[:len(tmp)//2]) + '\n' + ' '.join(tmp[len(tmp)//2:]))
                return text

            draw.text(500, 150, splitText(toptext))

            tmp_bottom = splitText(bottomtext)
            metrics = draw.get_font_metrics(i, tmp_bottom, multiline=True)
            draw.text(500, 1000 - int(metrics.text_height), tmp_bottom)

            draw(i)
            image_id = yield from bot._client.upload_image(io.BytesIO(i.make_blob(format="jpeg")), filename=meme+'.jpg')
            yield from bot.coro_send_message(event.conv.id_, None, image_id=image_id)
