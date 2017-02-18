import asyncio
import plugins
import logging

logger = logging.getLogger(__name__)

def _initialise(bot):
    plugins.register_user_command(["clear"])

def clear(bot, event, *args):
    if event.user.is_self:
        return
    yield from bot.coro_send_message(event.conv_id, ("\n"*100) + ".")
