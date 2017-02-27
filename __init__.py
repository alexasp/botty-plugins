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
                    #TODO: få error som dette til chatten
                    logger.info("Failed to load " + plug_path)
                    logger.info(str(e))

    loop = asyncio.get_event_loop()
    loop.create_task(init_botty())
