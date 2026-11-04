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


def ascii_safe(data):
    """Return data as a native str with non-ASCII characters replaced by '?'.

    Twisted wants a native str (bytes on python 2, text on python 3). This
    routine accepts either bytes (decoded as UTF-8) or text, so it never
    raises an exception on odd input. (Haven't fully tested on python 2 but
    trying to keep backwards compatibility.)
    """
    if isinstance(data, bytes):
        data = data.decode('utf-8', 'replace')

    data = data.encode('ascii', 'replace')

    if not isinstance(data, str):
        # python 3: back from bytes to text
        data = data.decode('ascii')
    return data
