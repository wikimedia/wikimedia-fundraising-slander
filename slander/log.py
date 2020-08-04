import sys
import syslog


def debug(msg):
    _log(syslog.LOG_DEBUG, msg)


def info(msg):
    _log(syslog.LOG_INFO, msg)


def error(msg):
    _log(syslog.LOG_ERR, msg)


def _log(priority, msg):
    syslog.openlog("slander", logoption=syslog.LOG_PID)
    syslog.syslog(priority, msg)
    syslog.closelog()

    if sys.stdout.isatty():
        print(msg)
