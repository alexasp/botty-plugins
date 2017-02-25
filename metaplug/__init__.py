import plugins
import logging
import io, asyncio, os, re
from asyncio.subprocess import PIPE

logger = logging.getLogger(__name__)

def _initialise(bot):
    plugins.register_handler(on_botting, type="sending", priority=1)
    plugins.register_admin_command(["pulltheplugs"])
    plugins.register_user_command(["tuklecheck", "amioutdated", "versionof"])

def versionof(bot, event, *args):
    if event.user.is_self:
        return

    if len(args) == 0:
        yield from bot.coro_send_message(event.conv_id, "cannot check the version of nothing")
        return

    plug = args[0].strip()
    try:
        guid = yield from bot.call_shared(plug + ".version", bot)
        yield from bot.coro_send_message(event.conv_id, "<b>Plugin: </b><i>" + plug  + "</i> was loaded with commit guid " + guid)
        current_guid = yield from get_last_commit()
        if guid != current_guid:
            yield from bot.coro_send_message(event.conv_id, "Plugin is not up to date!\n <b>current commit guid:</b> " + current_guid)
    except Exception as e:
        logger.info(e)
        yield from bot.coro_send_message(event.conv_id, "I've not registerd that " + plug + " was loaded")

def get_last_commit():
    proc = yield from asyncio.create_subprocess_exec(*["git", "rev-parse", "--verify", "HEAD"],
        stdout=PIPE, stderr=PIPE, env=dict(os.environ), cwd="hangupsbot/plugins/botty-plugins/")
    stdout, err = yield from proc.communicate()
    logger.info(err.decode())
    return stdout.decode()

def on_botting(bot, broadcast_list, context):
    segments = broadcast_list[0][1]

    if "botty-plugins" in segments[0].text:
        if "loaded" in segments[1].text or "reloaded" in segments[1].text:
            botty_plug = re.findall(r"(?<=botty\-plugins\.)\w*", segments[0].text)[0]
            current_guid = get_last_commit()
            bot.register_shared(botty_plug + ".version", lambda x: current_guid)

    if "reloading config.json" == segments[0].text:
        plugs = bot.config["plugins"]
        for plug in plugs:
            logger.info(plug)
            tmp = re.findall(r"(?<=botty\-plugins\.)\w*", plug)
            if len(tmp) > 0:
                botty_plug = tmp[0]
                current_guid = get_last_commit()
                bot.register_shared(botty_plug + ".version", lambda x: current_guid)


def amioutdated(bot, event, *args):
    if event.user.is_self:
        return

    proc = yield from asyncio.create_subprocess_exec(*["git", "remote", "update"],
        stdout=PIPE, stderr=PIPE, env=dict(os.environ), cwd="hangupsbot/plugins/botty-plugins/")
    stdout, err = yield from proc.communicate()
    yield from bot.coro_send_message(event.conv_id, err.decode())

    proc = yield from asyncio.create_subprocess_exec(*["git", "show-branch", "*master"],
        stdout=PIPE, stderr=PIPE, env=dict(os.environ), cwd="hangupsbot/plugins/botty-plugins/")
    stdout, err = yield from proc.communicate()
    status = stdout.decode()
    yield from bot.coro_send_message(event.conv_id, err.decode())
    yield from bot.coro_send_message(event.conv_id, stdout.decode())

def pulltheplugs(bot, event, *args):
    if event.user.is_self:
        return

    if len(args) == 2 and " ".join(args) == "with reset":
        proc = yield from asyncio.create_subprocess_exec(*["git", "reset", "--hard"],
            stdout=PIPE, stderr=PIPE, env=dict(os.environ), cwd="hangupsbot/plugins/botty-plugins/")
        stdout, err = yield from proc.communicate()
        status = stdout.decode()
        yield from bot.coro_send_message(event.conv_id, err.decode())
        yield from bot.coro_send_message(event.conv_id, stdout.decode())


    proc = yield from asyncio.create_subprocess_exec(*["git", "pull", "--no-commit", "--no-edit"],
        stdout=PIPE, stderr=PIPE, env=dict(os.environ), cwd="hangupsbot/plugins/botty-plugins/")
    stdout, err = yield from proc.communicate()
    status = stdout.decode()
    yield from bot.coro_send_message(event.conv_id, err.decode())
    yield from bot.coro_send_message(event.conv_id, stdout.decode())


def tuklecheck(bot, event, *args):
    if event.user.is_self:
        return

    proc = yield from asyncio.create_subprocess_exec(*["git", "status", "--short", "--", "."],
        stdout=PIPE, stderr=PIPE, env=dict(os.environ), cwd="hangupsbot/plugins/botty-plugins/")
    stdout, err = yield from proc.communicate()
    status = stdout.decode()
    yield from bot.coro_send_message(event.conv_id, err.decode())

    tukled_plugs = re.findall(r"(?<=M\s)\w*", status)
    if len(tukled_plugs) > 0:
        yield from bot.coro_send_message(event.conv_id, "<i>someone</i> has been tukling with: <b>" + "</b>, <b>".join(tukled_plugs) + "</b>")
    else:
        yield from bot.coro_send_message(event.conv_id, "no tukling noticed")
