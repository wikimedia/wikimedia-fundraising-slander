#!/usr/bin/env python3

from setuptools import setup

setup(
    name='slander',
    version='0.2',
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
