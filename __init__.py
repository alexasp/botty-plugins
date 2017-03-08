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
    "whereto"
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
    for plug in plugs:
        plug_path = "plugins.botty-plugins." + plug
        try:
            logger.info ("Loading: " + plug_path)
            plugins.load(bot, plug_path)
        except (RuntimeError, KeyError) as e:
            try:
                logger.info ("Reloading: " + plug_path)
                yield from plugins.unload(bot, plug_path)
                plugins.load(bot, plug_path)
            except (RuntimeError, KeyError) as e:
                if event is not None:
                    yield from bot.coro_send_message(event.conv_id, "Failed to load " + plug_path)
                    yield from bot.coro_send_message(event.conv_id, str(e))
                else:
                    logger.info("Failed to load " + plug_path)
                    logger.info(str(e))
    if event is not None:
        yield from bot.coro_send_message(event.conv_id, "<b>Botty reloaded</b>")
