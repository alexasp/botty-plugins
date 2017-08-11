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


memes = ["disgust","funi","insulted","china","weird","what","sad"]
logger = logging.getLogger(__name__)
current_dir = os.path.dirname(os.path.realpath(__file__))

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

    with Image(filename=current_dir+"/memes/"+meme+".jpg") as i:

        with Drawing() as draw:
            draw.stroke_color = Color('black')
            draw.fill_color = Color('white')
            draw.stroke_width = 5
            draw.text_alignment = 'center'
            draw.font = current_dir+'/impactreg.ttf'
            draw.font_size = 112
            draw.gravity = 'center'
            draw.text_antialias = True

            def splitText(text):
                metrics = draw.get_font_metrics(i, text, multiline=False)
                if(metrics.text_width > 900):
                    tmp = text.split(' ')
                    if len(tmp) == 1: return splitText(tmp[0][::2]) + '...\n' + splitText(tmp[0][1::2])
                    return splitText(' '.join(tmp[:len(tmp)//2])) + '\n' + splitText(' '.join(tmp[len(tmp)//2:]))
                return text

            def scaleText(text):
                tmp = splitText(text)
                metrics = draw.get_font_metrics(i, tmp, multiline=True)
                if (metrics.text_height > 350 or metrics.text_width > 1000) and draw.font_size > 40:
                    draw.font_size = draw.font_size - 20
                    return scaleText(text)
                else:
                    return tmp

            draw.font_size = 160
            tmp_top = scaleText(toptext)
            metrics = draw.get_font_metrics(i, tmp_top, multiline=True)
            draw.text(500, 10 + int(metrics.character_height), tmp_top)

            draw.font_size = 160
            tmp_bottom = scaleText(bottomtext)
            metrics = draw.get_font_metrics(i, tmp_bottom, multiline=True)
            draw.text(500, 980 + int(metrics.character_height) - int(metrics.text_height), tmp_bottom)

            draw(i)
            image_id = yield from bot._client.upload_image(io.BytesIO(i.make_blob(format="jpeg")), filename=meme+'.jpg')
            yield from bot.coro_send_message(event.conv.id_, None, image_id=image_id)
