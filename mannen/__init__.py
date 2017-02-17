import urllib, json
import plugins
import logging

url = "http://harmannenfaltned.no/api"

logger = logging.getLogger(__name__)

def _initialise(bot):
    plugins.register_user_command(["harmannenfalt"])


def harmannenfalt(bot, event, *args):
    if len(args) == 0:
        response = urllib.urlopen(url)
        data = json.load(response)
        falt = 'falt' if data['falt_ned'] else 'ikke falt'
        yield from bot.coro_send_message(event.conv_id, "Mannen har " + falt)
