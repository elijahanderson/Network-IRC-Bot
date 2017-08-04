# This IRC Bot will access an IRC channel (#newcoder on freenode.net for this one) and be able
# to chat with users if they use certain commands

# twisted is an event-driven networking module that has vast capabilities in networking.

# I'll use twisted's protocol module to create the bot factory [explain later here]
# BTW, a protocol in CS is just a set of rules for transmitting data between electronic devices
#   -- this one specifically is for Internet Relay Chat (IRC)
from twisted.internet import protocol

# twisted's log module is going to be used for logging (since this bot is event-driven I will need to
# log in certain actions)
from twisted.python import log

# twisted's irc module is used so I don't have to reinvent the wheel
from twisted.words.protocols import irc

# Two classes will be created:
#       1) TalkBackBot -- defines the bot's behavior
#       2) TalkBackBotFactory -- instantiates the bot

class TalkBackBotFactory(protocol.ClientFactory) :

    # instantiate the TalkBotBot IRC protocol
    # this calls an internal method within the twisted.internet.protocol library, buildProtocol()
    # it instantiates a ClientFactory to be able to handle input of an incoming server connection
    protocol = TalkBackBot

    # Initialize the bot factory with our settings.
    def __init__(self, channel, nickname, realname, responses, triggers) :
        self.channel = channel
        self.nickname = nickname
        self.realname = realname
        self.responses = responses
        self.triggers = triggers


# TalkBackBot class makes use of irc.IRCClient from twisted to make use of its inherited functions

class TalkBackBot(irc.IRCClient) :

    # this is called when a connection is made
    # this is considered the initialization of the protocol because it is called when the connection
    # from our client to the IRC server is completed
    def connectionMade(self) :
        self.nickname = self.factory.nickname
        self.realname = self.factory.realname

        # takes in the whole TalkBackBot object, which contains the nickname and realname variables
        irc.IRCClient.connectionMade(self)

        # for debugging purposes - if there is an issues connecting to the server, this message won't pop up
        log.msg('connectionMade')


    # called when a connection is lost
    def connectionLost(self, reason) :
        irc.IRCClient.connectionLost(self, reason)

        # the curly braces indicate a replacement field, which contains reason
        # the !r tells format() to call repr() instead of str(), so that format() will include quotes around reason
        # where str() is designed to be readable, repr() is designed to be unambiguous
        log.msg('connectionLost {!r}'.format(reason))


    #######################
    # callbacks for events#
    #######################

    # called when bot has successfully signed on to server -- different than just connecting (treated as protocol setup)
    def signedOn(self) :
        log.msg('Signed on')

        # in case there is another user or bot signed on with the same nickname
        # the server will give the bot a new nickname with a trailing _, like eli_
        if self.nickname != self.factory.nickname :
            log.msg('Your nickname was already occupied, actual nickname is ' 
                    '"{}".'.format(self.nickname))

        # self.join() is defined in irc.IRCClient -- actually joins our desired channel
        self.join(self.factory.channel)


    # called when bot joins the channel
    def joined(self, channel) :
        log.msg('[{nick} has joined {channel}]'
                .format(nick=self.nickname, channel=self.factory.channel))

    # this function actually defines what happens when someone sends the bot a message
    def privmsg(self, user, channel, msg) :

        # first, initialize who the bot is replying to, the prefix for our reply message, and
        # the nickname of the user who triggered the bot
        sendTo = None
        prefix = ''
        senderNick = user.split('!', 1)[0]

        # for the condition when the bot receives a private message, like with /msg
        if channel == self.nickname :
            # send a PM back to the sender
            sendTo = senderNick

        # for when a user starts a message with the bot's nickname within the channel
        elif msg.startswith(self.nickname) :
            # reply back on the channel
            sendTo = channel
            prefix = senderNick + ': '

        # if someone in the channel says the trigger, ( for this bot, !test )
        else :
            msg = msg.lower()

            for trigger in self.factory.triggers :
                if msg in trigger :
                    sendTo = channel
                    prefix = senderNick + ': '
                    break

        # if none of the conditions are met and sendTo is still None, nothing happens
        if sendTo :
            # pick a random response using response_picker.py
            response = self.factory.responses.pick()
            # msg() is defined in irc.IRCClient
            self.msg(sendTo, prefix + response)

            log.msg('Sent message to {receiver}, triggered by {sender}: \n\t{response}'
                    .format(receiver=sendTo, sender=senderNick, response=response))
