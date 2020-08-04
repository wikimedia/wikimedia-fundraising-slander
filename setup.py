#!/usr/bin/env python3

from distutils.core import setup

setup(
    name='slander',
    version='0.1',
    install_requires=[
        'feedparser',
        'irc',
        'pyOpenSSL',
        'PyYAML',
        'service-identity',
        'twisted',
    ],
    url='https://gerrit.wikimedia.org/g/wikimedia/fundraising/slander/+/refs/heads/master',
    scripts=['scripts/slander'],
    packages=['slander']
)
