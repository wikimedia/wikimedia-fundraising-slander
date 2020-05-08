"""Helpers for text manipulation"""

import re
import sys

if (sys.version_info > (3, 0)):
    # Python 3 code in this block
    from html.parser import HTMLParser
else:
    # Python 2 code in this block
    from HTMLParser import HTMLParser


maxlen = 200


def strip(msg, html=True, space=True, truncate=False):
    class MLStripper(HTMLParser):
        def __init__(self):
            self.reset()
            self.fed = []

        def handle_data(self, d):
            self.fed.append(d)

        def get_data(self):
            return ''.join(self.fed)

    if html:
        stripper = MLStripper()
        stripper.feed(msg)
        msg = stripper.get_data()
    if space:
        msg = re.sub(r"\s+", " ", msg).strip()
    if truncate:
        msg = trunc(msg)
    return msg


def abbrevs(name):
    """
    Turn a space-delimited name into initials, e.g. Frank Ubiquitous Zappa ->
    FUZ
    """
    return "".join([w[:1] for w in name.split()])


def trunc(message):
    if len(message) > maxlen:
        return (message[:(maxlen-3)] + "...")
    else:
        return message
