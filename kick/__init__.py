import os
import plugins
import logging
import io, random
from commands import command

logger = logging.getLogger(__name__)

def _initialise(bot):
    plugins.register_user_command(["kick"])


def kick(bot, event, *args):
    if event.user.is_self:
        return

    if len(args) == 0:
        yield from bot.coro_send_message(event.conv_id, "pliz supply someone to kick")

    remove = []
    for arg in args:
        try:
            user = bot.call_shared("find_user", bot, arg)
            if user is not None:
                yield from bot.coro_send_message(event.conv_id, "Kicking " + user.full_name + (" in the plums" if random.randint(0,2) == 1 else ""))
                remove.append(user.id_.chat_id)
        except Exception as e:
            yield from bot.coro_send_message(event.conv_id, "I need shamebells to werk")
            return
            logger.info(e)

    source_conv = event.conv.id_
    arguments = ["refresh", source_conv, "without"] + remove + ["norename", "quietly", "test"]
    yield from command.run(bot, event, *arguments)
