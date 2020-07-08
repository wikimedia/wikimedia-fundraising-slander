import datetime

from twisted.words.protocols import irc
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet.ssl import ClientContextFactory
from twisted.internet import reactor

import brain
import job
import log
import text


class RelayToIRC(irc.IRCClient):
    """
    Wire bot brain, job queue, and config into a Twisted IRC client
    """
    timestamp = None

    def connectionMade(self):
        self.config = self.factory.config
        self.nickname = self.config["irc"]["nick"]
        self.realname = self.config["irc"]["realname"]
        self.channel = self.config["irc"]["channel"]
        if "channel_key" in self.config["irc"]:
            self.channel_key = self.config["irc"]["channel_key"]
        else:
            self.channel_key = ""
        if "maxlen" in self.config["irc"]:
            text.maxlen = self.config["irc"]["maxlen"]

        self.sourceURL = self.config["source_url"]

        irc.IRCClient.connectionMade(self)

        if "pass" in self.config["irc"]:
            if "ownermail" in self.config["irc"]:
                cmd = "REGISTER {password} {addr}".format(
                    password=self.config["irc"]["pass"],
                    addr=self.config["irc"]["ownermail"]
                )
                self.msg("NickServ", cmd)
            elif "regverify" in self.config["irc"]:
                cmd = "VERIFY REGISTER {nick} {verify}".format(
                    nick=self.config["irc"]["nick"],
                    verify=self.config["irc"]["regverify"]
                )
                self.msg("NickServ", cmd)
            cmd = "IDENTIFY {pw}".format(pw=self.config["irc"]["pass"])
            self.msg("NickServ", cmd)

    def signedOn(self):
        self.join(self.channel, self.channel_key)

    def joined(self, channel):
        log.info("Joined channel %s as %s" % (channel, self.nickname))
        self.brain = brain.Brain(self.config, sink=self)
        # XXX get outta here:
        source = job.JobQueue(
            definition=self.config["jobs"],
            sink=self,
            interval=self.config["poll_interval"]
        )
        source.run()

    def privmsg(self, user, channel, message):
        if not self.config["deaf"] and message.find(self.nickname) >= 0:
            self.brain.respond(user, message)

    def write(self, data):
        if isinstance(data, list):
            for line in data:
                self.write(line)
            return
        self.say(self.channel, data.encode('ascii', 'replace'))
        self.timestamp = datetime.datetime.utcnow()

    @staticmethod
    def run(config):
        factory = ReconnectingClientFactory()
        factory.protocol = RelayToIRC
        factory.config = config
        if (config["irc"]["ssl"] is True):
            sslClientContextFactory = ClientContextFactory()
            log.info("connecting to %s:%s using ssl" % (
                config["irc"]["host"], config["irc"]["port"]
            ))
            reactor.connectSSL(
                config["irc"]["host"],
                config["irc"]["port"],
                factory,
                sslClientContextFactory
            )
        else:
            log.info("connecting to %s:%s" % (
                config["irc"]["host"], config["irc"]["port"]
            ))
            reactor.connectTCP(
                config["irc"]["host"],
                config["irc"]["port"],
                factory
            )
        reactor.run()
