Relay feed and vcs activities to an IRC channel.

Installation
============

    git clone https://gerrit.wikimedia.org/r/wikimedia/fundraising/slander

    pip install twisted feedparser PyYAML irc pyOpenSSL service-identity

OR

    apt-get install python-twisted python-feedparser python-yaml python-irclib python-openssl python-service-identity

Configuration
=============

Config files are written in YAML, and are usually kept in the user's ".slander" or in /etc/slander

Here's an example configuration file--note that YAML is whitespace-sensitive,
requires spaces, not tabs, and alignment must be preserved...

	# List all jobs, keyed by type (FIXME: we should allow more than one per type)
    jobs:
	tail:
		path: /var/log/meltdown

		# Trim some extraneous stuff from the loglines.
		massage_regexes:
			- "(?xi) ^ [A-Za-z]{3} \s+ \d+": ""
			- "log_to_irc\[\d+\]": ""

    irc:
        host: irc.freenode.net
        port: 6667
        #ssl: True
        nick: civi-activity
        # Optional unless your bot is registered
        pass: FOO
        realname: CiviCRM svn and jira notification bot
        # Note that quotes are necessary around #channames
        channel: "#civicrm-test"
        # Truncate messages longer than this many characters
        maxlen: 200

    # Measured in seconds
    poll_interval: 60

    # Override the builtin URL if you've forked this project, so people know
    # how to contribute.
    source_url: https://gerrit.wikimedia.org/g/wikimedia/fundraising/slander/+/refs/heads/master

Running
=======

To start the bot, call

    ./slander/slander.py

If you want to specify a config file, pass it as an argument:

    ./slander/slander.py /etc/slander/PROJ.yaml

Alternatively, you can give just the project name, and slander will look in /etc/slander/PROJ.yaml:

    ./slander/slander.py PROJ

Credits
=======
IRC code adapted from Miki Tebeka's http://pythonwise.blogspot.com/2009/05/subversion-irc-bot.html

Markup stripper from Eloff's http://stackoverflow.com/a/925630

Forked from https://github.com/adamwight/slander

The project homepage is https://gerrit.wikimedia.org/g/wikimedia/fundraising/slander/+/refs/heads/master
