import plugins

plugs = [
    "metaplug",
    "askdonald",
    "askwolfy",
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
        plugins.unload(bot, "plugins.botty-plugins." + plug)
        plugins.load(bot, "plugins.botty-plugins." + plug)
