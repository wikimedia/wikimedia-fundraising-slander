import feedparser

from . import log


class FeedPoller(object):
    """
    Generic RSS/Atom feed watcher
    """

    last_seen_id = None

    def __init__(self, source=None):
        log.info(f"Initializing feed poller: {source}")
        self.source = source

    def check(self):
        result = feedparser.parse(self.source)
        # https://feedparser.readthedocs.io/en/latest/bozo/
        if result.get('bozo') and not result.entries:
            log.error(f"Failed to parse feed {self.source}: {result.get('bozo_exception')}")
            return []
        entries = list(reversed(result.entries))
        new = []
        skipping = True
        for entry in entries:
            if self.last_seen_id == self.entry_id(entry):
                skipping = False
            elif not skipping:
                new.append(self.parse(entry))

        # Advance even if some entries were odd, so a bad entry is not
        # retried (and earlier ones re-posted) on every poll.
        if entries:
            self.last_seen_id = self.entry_id(entries[-1])
        return new

    @staticmethod
    def entry_id(entry):
        return entry.get('id') or entry.get('link') or entry.get('title')

    def parse(self, entry):
        return f"{entry.get('summary', '')} [{entry.get('link', '')}]"
