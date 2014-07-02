import copy
import re
from twisted.internet.task import LoopingCall

import log


class JobQueue(object):
    """Create and poll jobs"""

    threads = []
    jobs_def = []

    def __init__(self, definition, sink, interval):
        """Read job definitions from a config source, create an instance of the
        job using its configuration, and store the config for reference.
        """
        self.sink = sink
        self.interval = interval
        JobQueue.jobs_def = []
        for type_name, options in definition.items():
            classname = type_name.capitalize() + "Poller"
            m = __import__(type_name, fromlist=[classname])
            if hasattr(m, classname):
                klass = getattr(m, classname)
                job = klass(**options)
                job.config = copy.deepcopy(options)
                job.config['class'] = type_name
                JobQueue.jobs_def.append(job)
            else:
                raise Exception("Failed to create job of type " + classname)

    @staticmethod
    def describe():
        jobs_desc = ", ".join(
            [("%s: %s" % (j.config['class'], j.config))
                for j in JobQueue.jobs_def]
        )
        return jobs_desc

    def check(self):
        for job in JobQueue.jobs_def:
            for line in job.check():
                if line:
                    line = self.massage_content(line, job)
                    self.sink.write(line)

    def massage_content(self, line, job):
        """Do job-specific munging of the output line, when configured"""

        if "massage_regexes" in job.config:
            for masseuse in job.config["massage_regexes"]:
                from_re, to_str = masseuse.items()[0]
                line = re.sub(from_re, to_str, line)

        return line

    @staticmethod
    def killall():
        for old in JobQueue.threads:
            old.stop()
        JobQueue.threads = []

    def run(self):
        JobQueue.killall()
        task = LoopingCall(self.check)
        JobQueue.threads = [task]
        task.start(self.interval)
        log.info("Started polling jobs, every %d seconds." % (self.interval, ))
