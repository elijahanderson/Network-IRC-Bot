# to set up plugin, we need a way to parse our settings configuration
# for this, use ConfigParser from Python's standard library
from ConfigParser import ConfigParser

# 3rd party modules
from twisted.application.service import IServiceMaker, Service
from twisted.internet.endpoints import clientFromString
from twisted.plugin import IPlugin
from twisted.python import usage, log
# implementer will be used as a Python decorator, which twisted treats as an interface
from zope.interface import implementer

# user modules
from talkback.bot import TalkBackBotFactory
from talkback.response_picker import ResponsePicker


# first, use twisted's usage module to parse our configuration

class Options(usage.Options) :
    # to tell our twisted app about the options it can handle:
    optParameters = [
        ['config', 'c', 'settings.ini', 'Configuration file.']
    ]


# the class that constructs our application using twisted's service class to start/stop our app

class TalkBackBotService(Service) :

    # create private var _bot (underscore indicates private) with value None
    _bot = None

    # this is called when BotServiceMaker returns TalkBackBotService in makeService()
    def __init__(self, endpoint, channel, nickname, realname, triggers) :
        self._endpoint = endpoint
        self._channel = channel
        self._nickname = nickname
        self._realname = realname
        self._triggers = triggers

    # construct a client & connect to server
    def startService(self) :
        # construct a client & connect to server
        # nested import to avoid installing the default reactor
        from twisted.internet import reactor

        # assigns private var _bot to the passed-in parameter, bot
        def connected(bot) :
            self._bot = bot

        #
        def failure(err) :
            log.err(err, _why='Could not connect to specified server.')
            reactor.stop()

        responses = ResponsePicker()

        # define a client that constructs an endpoint based on a string with clientFromString function
        # clientFromString takes in the reactor that was imported and the endpoint (defined in settings.ini)
        client = clientFromString(reactor, self._endpoint)

        # instantiate TalkBackBotFactory defined in boy.py
        factory = TalkBackBotFactory(
            self._channel,
            self._nickname,
            self._realname,
            responses,
            self._triggers
        )

        # return client, connected to the endpoint with the factory variable
        # addCallBacks() takes a pair of functions of what happens on success/failure
        return client.connect(factory).addCallbacks(connected, failure)

    # disconnect -- triggered when service closes connection between client and server
    def stopService(self) :

        # if the connection is not the bot's fault:
        if self._bot and self._bot.transport.connected :
            self._bot.transport.loseConnection()


# to go along with TalkBackBotService, make a Maker class (similar to how the bot Factory class
# creates our bot) that constructs our service
# Remember, implementer is used as a Python decorator - it's used as a marker saying that
# BotServiceMaker() implements the following arguments as interfaces
""" So the below is equivalent to:
    class BotServiceMaker(object):
        code
    BotServiceMaker = implementer(BotServiceMaker)"""

@implementer(IServiceMaker, IPlugin)
class BotServiceMaker(object) :
    # tapname is the short string name for our plugin; it is a subcommand of twisted
    tapname = 'twsrs'

    # description is the short summary of what the plugin does
    description = 'My first IRC bot'

    # options refers to our Options class
    options = Options

    # construct the talkbackbot service
    def makeService(self, options):

        # instantiate ConfigParser()
        config = ConfigParser()

        # read from the options parameter that we pass in to grab 'config' in options
        # essentially, this grabs and reads settings.ini
        config.read([options['config']])

        # create list comprehension for triggers
        triggers = [
            # strip the null characters for every trigger
            trigger.strip()
            for trigger
            # get our triggers from settings.ini
            in config.get('talkback', 'triggers').split('\n')
            if trigger.strip()
        ]

        # return an instantiated TalkBackBotService class with parameters grabbed from the config var
        return TalkBackBotService(
            endpoint=config.get('irc', 'endpoint'),
            channel=config.get('irc', 'channel'),
            nickname=config.get('irc', 'nickname'),
            realname=config.get('irc', 'realname'),
            triggers=triggers
        )

# construct an object which provides the relevant interfaces
# The name of this variable is irrelevant
serviceMaker = BotServiceMaker()
