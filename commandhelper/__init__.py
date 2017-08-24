
import plugins, logging, commands
from difflib import SequenceMatcher
from utils import simple_parse_to_segments
import shlex
from random import randint

logger = logging.getLogger(__name__)
command_tried = {}
command_suggested = {}

def _initialise(bot):
    plugins.register_handler(intercept_command, type="message", priority=1)
    plugins.register_handler(intercept_reply, type="sending", priority=2)

def intercept_command(bot, event, command):
    global command_tried

    if event.text.startswith('/bot'):
        if event.conv_id in command_suggested:
            command_suggested[event.conv_id] = None

        tmp = event.text.split(' ')
        if len(tmp) > 1:
            command_tried[event.conv_id] = {
                'command': tmp[1],
                'arguments': " ".join(tmp[2:]) if len(tmp) > 2 else None,
                'chat_id': event.user_id.chat_id
            }
    elif event.conv_id in command_suggested and command_suggested[event.conv_id]["chat_id"] == event.user_id.chat_id:
        if "yes i did" == event.text.lower().strip():
            yield from commands.command.run(bot, event, *command_suggested[event.conv_id]["command"])

def intercept_reply(bot, broadcast_list, context):
    global command_tried
    orig_broadcast_list = broadcast_list[:]
    for broadcast in orig_broadcast_list:
        conv_id = broadcast[0]

        if conv_id in command_tried:
            chat_segments = broadcast[1]
            for segment in chat_segments:
                if "Unknown Command" in segment.text:
                    suggestion = getsuggestion(bot, conv_id, command_tried[conv_id])
                    if suggestion is not None:
                        user = bot.get_hangups_user(command_tried[conv_id]["chat_id"])
                        if "orten" in user.full_name.lower():
                            broadcast_list.append((conv_id, simple_parse_to_segments(random_finger_insult())))
                        broadcast_list.append((conv_id, simple_parse_to_segments("".join(["Did you mean '", suggestion, "'?"]))))
                    command_tried[conv_id] = None

def getsuggestion(bot, conv_id, command):
    all_commands = commands.command.get_available_commands(bot, command["chat_id"], conv_id)
    match = {
        "likeness": 0,
        "actual_command": None
    }

    def test_likeness (test_list):
        for test_command in test_list:
            likenss = SequenceMatcher(None, test_command, command["command"]).ratio()
            if likenss > match["likeness"]:
                match["likeness"] = likenss
                match["actual_command"] = test_command

    test_likeness(all_commands["admin"])
    test_likeness(all_commands["user"])

    if(match["likeness"] < 0.6):
        return None

    actual_command = match["actual_command"]
    global command_suggested
    command_suggested[conv_id] = {
        "chat_id": command["chat_id"],
        "command": [actual_command] + (shlex.split(command["arguments"]) if command["arguments"] is not None else [])
    }
    return " ".join(["/bot", actual_command, command["arguments"] if command["arguments"] is not None else ''])

def random_finger_insult():
    insults = ["lol fingers so fat", "fatty fingers", "typing so hard lol", "Andy duno how to write"]
    return insults[randint(0, len(insults)-1)]
