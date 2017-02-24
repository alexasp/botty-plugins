import os
import plugins
import logging
import io

def _initialise(bot):
    plugins.register_user_command(["kick"])


def kick(bot, event, *args):
    parameters = list(args)

    if "andre" in " ".join(args):
        yield from bot.coro_send_message(event.conv_id, "Du kan ikke kicke i hytt og gevær")
        return
        
    source_conv = event.conv_id
    remove = []

    if len(remove) <= 0:
        raise ValueError(_("supply at least one valid user id to kick"))

    for parameter in parameters:
        if parameter in bot.conversations.catalog:
            source_conv = parameter
        elif parameter in bot.conversations.catalog[source_conv]["participants"]:
            remove.append(parameter)
        else:
            raise ValueError(_("supply optional conversation id and valid user ids to kick"))

    arguments = ["refresh", source_conv, "without"] + remove

    if test:
        arguments.append("test")

    if quietly:
        arguments.append("quietly")

    yield from command.run(bot, event, *arguments)