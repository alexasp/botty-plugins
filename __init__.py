import plugins, logging
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


def _initialise(bot):
    for plug in plugs:
        try:
            plugins.unload(bot, "plugins.botty-plugins." + plug)
            plugins.load(bot, "plugins.botty-plugins." + plug)
        except (RuntimeError, KeyError) as e:
            logger.info(str(e))
