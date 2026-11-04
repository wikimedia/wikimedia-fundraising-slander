import datetime
import re

from twisted.words.protocols import irc
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet import ssl
from twisted.internet import reactor

from . import brain
from . import job
from . import log
from . import text


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
        self.configure_flood_control()
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
        self.mode(self.nickname, True, "B")
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
        # Only answer in our own channel (not private messages) and only when
        # directly addressed: "nick: cmd".
        if self.config["deaf"] or channel.lower() != self.channel.lower():
            return
        addressed = re.match(
            r"^\s*%s\s*:\s*(.*)" % re.escape(self.nickname),
            message,
            re.IGNORECASE
        )
        if addressed:
            self.brain.respond(user, addressed.group(1))

    def configure_flood_control(self, clock=reactor):
        """Throttle and cap relayed output so a burst of log lines or a big
        feed won't flood the channel or get the bot k-lined."""
        irc_config = self.config["irc"]
        # Seconds between lines sent to the server (Twisted queues the rest)
        self.lineRate = float(irc_config.get("line_rate", 1.0))
        # Max relayed lines per window; the rest are counted and summarized
        self.max_lines = int(irc_config.get("max_lines", 20))
        self.window = float(self.config.get("poll_interval", 60))
        self.clock = clock
        self.window_start = clock.seconds()
        self.sent_in_window = 0
        self.suppressed = 0
        self.flush_call = None

    def write(self, data):
        if isinstance(data, list):
            for line in data:
                self.write(line)
            return
        now = self.clock.seconds()
        if now - self.window_start >= self.window:
            self.window_start = now
            self.sent_in_window = 0

        if self.sent_in_window >= self.max_lines:
            self.suppressed += 1
            if self.flush_call is None:
                delay = self.window_start + self.window - now
                self.flush_call = self.clock.callLater(
                    delay, self.report_suppressed)
            return

        self.sent_in_window += 1
        line = text.trunc(data)
        self.say(self.channel, line.encode('ascii', 'replace'))
        self.timestamp = datetime.datetime.utcnow()

    def report_suppressed(self):
        self.flush_call = None
        if self.suppressed:
            log.error("Flood control dropped %d lines" % (self.suppressed, ))
            self.say(self.channel, "[flood control: %d more lines dropped]"
                     % (self.suppressed, ))
            self.suppressed = 0

    @staticmethod
    def run(config):
        factory = ReconnectingClientFactory()
        factory.protocol = RelayToIRC
        factory.config = config
        if (config["irc"]["ssl"] is True):
            log.info("connecting to %s:%s using ssl" % (
                config["irc"]["host"], config["irc"]["port"]
            ))
            reactor.connectSSL(
                config["irc"]["host"],
                config["irc"]["port"],
                factory,
                tls_options(config["irc"]["host"])
            )
        else:
            if "pass" in config["irc"] or "channel_key" in config["irc"]:
                log.error("WARNING: sending IRC credentials without TLS. "
                          "Set irc.ssl to True and use port 6697.")
            log.info("connecting to %s:%s" % (
                config["irc"]["host"], config["irc"]["port"]
            ))
            reactor.connectTCP(
                config["irc"]["host"],
                config["irc"]["port"],
                factory
            )
        reactor.run()


def tls_options(host):
    """TLS client options that verify the server certificate against the
    system trust store and check that it matches the hostname."""
    if isinstance(host, bytes):
        host = host.decode("ascii")
    return ssl.optionsForClientTLS(hostname=host)
