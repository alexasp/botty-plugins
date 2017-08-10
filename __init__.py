import plugins, logging, time, asyncio
logger = logging.getLogger(__name__)

plugs = [
    "metaplug",
    "askdonald",
    "askwolfy",
    "botender",
    "dangerzone",
    "imgur",
    "insulter",
    "jiffy",
    #"kick",
    "mannen",
    "panic",
    "shamebell",
    "superecho",
    "tldrify",
    "whatis",
    "whereto",
    "botbiker",
    "botforecast",
    "autoposter",
    "swaptron",
    "andymemer"
]

#TODO:  /bot reload kaller ikke _initializse. Vet ikke om det er en bug men
#       workaround for botty plugs er å kjøre /bot pluginreload botty-plugins
def _initialise(bot):
    @asyncio.coroutine
    def init_botty():
        yield from reloadbotty(bot, None)

    loop = asyncio.get_event_loop()
    loop.create_task(init_botty())

    plugins.register_admin_command(["reloadbotty"])

def reloadbotty(bot, event, *args):
    errors = []
    plugs_loaded = []
    for plug in plugs:
        plug_path = "plugins.botty-plugins." + plug
        fail_msg = "<b>Failed to load " + plug + "</b>"
        try:
            logger.info ("Loading: " + plug_path)
            if plugins.load(bot, plug_path):
                plugs_loaded.append(plug)
            else:
                errors.append(fail_msg)
        except RuntimeError as e:
            try:
                logger.info ("Reloading: " + plug_path)
                yield from plugins.unload(bot, plug_path)
                if plugins.load(bot, plug_path):
                    plugs_loaded.append(plug)
                else:
                    errors.append(fail_msg)
            except Exception as e:
                errors.append(fail_msg)
        except Exception as e:
            errors.append(fail_msg)

    if event:
        if len(errors) == 0:
            yield from bot.coro_send_message(event.conv_id, "<b>Botty reloaded</b>")
            yield from bot.coro_send_message(event.conv_id, "\n".join(plugs_loaded))
        else:
            yield from bot.coro_send_message(event.conv_id, "\n".join(errors))
