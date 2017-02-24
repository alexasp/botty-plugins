
import asyncio, re, os
import plugins
import logging
import io, time, random

logger = logging.getLogger(__name__)

def _initialise(bot):
    plugins.register_user_command(["shame"])
    bot.register_shared("find_user", find_user)

def find_user(bot, search):
    all_known_users = {}
    for chat_id in bot.memory["user_data"]:
        all_known_users[chat_id] = bot.get_hangups_user(chat_id)

    search_lower = search.strip().lower()
    for u in sorted(all_known_users.values(), key=lambda x: x.full_name.split()[-1]):
        if( search_lower in u.full_name.lower() ):
            return u
    return None

def shame(bot, event, *args):
    if event.user.is_self:
        return

    if len(args) == 0:
        yield from bot.coro_send_message(event.conv_id, "I duno who to shame")
        return

    user = find_user(bot, " ".join(args))
    if user is None:
        yield from bot.coro_send_message(event.conv_id, "I duno who to shame, cannot find user " + " ".join(args))
        return

    conv_1on1 = None
    if user.full_name.split(" ")[0] == "Jens":
        yield from bot.coro_send_message(event.conv_id, "You cannot shame the king, shame on you")
        conv_1on1 = yield from bot.get_1to1(event.user.id_.chat_id)
        user = event.user
    else:
        conv_1on1 = yield from bot.get_1to1(user.id_.chat_id)

    yield from bot.coro_send_message(event.conv.id_, "Shaming " + user.full_name)

    l = random.randint(4,8)
    for i in range(0, l):
        yield from bot.coro_send_message(conv_1on1, "<b>shame</b>")
        if random.randint(0,1) == 0:
            yield from bot.coro_send_message(conv_1on1, "🔔🔔")
        yield from asyncio.sleep(1.0 + random.random())

    yield from bot.coro_send_message(event.conv.id_, user.full_name + " has been shamed")
