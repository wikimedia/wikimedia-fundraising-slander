import re

from . import log

# Top-level config keys that are safe to show in the channel.
PUBLIC_KEYS = ("source_url", "poll_interval", "mute", "deaf")


class Brain:
    """Respond to incoming commands"""

    def __init__(self, config, sink=None):
        self.config = config
        self.sink = sink
        self.source_url = self.config["source_url"]

    def say(self, message, force=False):
        if not force and self.config.get('mute'):
            log.info("muffling msg: " + message)
            return
        self.sink.say(self.sink.channel, message)

    def respond(self, user, message):
        if re.search(r'\bhelp\b', message):
            msg = f"Improve this project: {self.source_url}"
            self.say(msg)
        elif re.search(r'\bconfig\b', message):
            # Read-only, allowlisted summary. Never echo the raw config since
            # it holds secrets: NickServ password, channel key, etc.
            summary = ", ".join(
                f"{k}={self.config[k]}"
                for k in PUBLIC_KEYS if k in self.config
            )
            jobs = ", ".join(sorted(self.config.get("jobs", {})))
            self.say(f"Configuration: [{summary}, jobs={jobs}]", force=True)
        # elif re.search(r'\bkill\b', message):
        #     self.say(f"Squeal! Killed by {user}")
        #     job.JobQueue.killall()
        #     #self.quit()
        #     #self.factory.stopTrying()
        elif re.search(r'\blast\b', message):
            if self.sink.timestamp:
                self.say(f"My last post was {self.sink.timestamp} UTC")
            else:
                self.say("No activity.")
        else:
            log.error(f"Failed to handle IRC command: {user} said {message}")
