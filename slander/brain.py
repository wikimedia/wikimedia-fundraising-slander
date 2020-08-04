import re
import json

from . import job
from . import log


class Brain(object):
    """Respond to incoming commands"""

    def __init__(self, config, sink=None):
        self.config = config
        self.sink = sink
        if "irc" in self.config:
            if "ownermail" in self.config["irc"]:
                self.config["irc"]["ownermail"] = "xxx@example.com"
            if "regverify" in self.config["irc"]:
                self.config["irc"]["regverify"] = "*******"

        self.source_url = self.config["source_url"]

    def say(self, message, force=False):
        if not force and 'mute' in self.config and int(self.config['mute']):
            log.info("muffling msg: " + message)
            return
        self.sink.say(self.sink.channel, message)

    def respond(self, user, message):
        if re.search(r'\bhelp\b', message):
            msg = "Improve this project: {src}".format(src=self.source_url)
            self.say(msg)
        elif re.search(r'\bconfig\b', message):
            assignment_re = r"""(?x)
                \b
                (?P<name> [^=\s]+ )
                \s* = \s*
                (?P<value> \S+ )
            """
            match = re.search(assignment_re, message)
            if match:
                self.config[match.group('name')] = match.group('value')

            dump = self.config
            dump['jobs'] = job.JobQueue.describe()
            dumpstr = json.dumps(self.redact(dump))
            self.say(
                "Configuration: [{dump}]".format(dump=dumpstr),
                force=True
            )
        # elif re.search(r'\bkill\b', message):
        #     self.say("Squeal! Killed by %s" % (user, ))
        #     job.JobQueue.killall()
        #     #self.quit()
        #     #self.factory.stopTrying()
        elif re.search(r'\blast\b', message):
            if self.sink.timestamp:
                self.say("My last post was %s UTC" % (self.sink.timestamp, ))
            else:
                self.say("No activity.")
        else:
            log.error("Failed to handle IRC command: {user} said {msg}".format(
                user=user, msg=message
            ))

    def redact(self, data):
        FORBIDDEN_KEY_PATTERN = r'pw|pass|password'
        BLACKOUT = "p***word"

        for key, value in data.items():
            if re.match(FORBIDDEN_KEY_PATTERN, key):
                data[key] = BLACKOUT
            elif hasattr(value, 'items'):
                data[key] = self.redact(value)

        return data
