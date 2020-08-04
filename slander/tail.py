import os
import os.path

from . import log


class TailPoller(object):
    """Tail -f a file as the message source"""

    def __init__(self, path=None, **kw):
        log.info("Initializing file tailer on: [{path}]".format(path=path))

        self.path = path
        self.inode = os.stat(self.path).st_ino
        self.file = None

        self.reload()

        # fast-forward to the end-of-file
        self.file.seek(0, 2)

        self.output_buffer = []

    def reload(self):
        """Check the file status and reopen if we have been rotated out"""

        if self.file:
            if os.stat(self.path).st_ino != self.inode:
                log.info("Logfile has rotated!  Refreshing...")
                # dump any new lines before closing the old file
                self.read()
                self.file = None

        if not self.file:
            self.file = open(self.path, "r")
            self.inode = os.fstat(self.file.fileno()).st_ino

    def check(self):
        """Check for logfile rotation, return all new lines"""

        try:
            self.reload()
            self.read()
        except IOError as ex:
            log.error(ex)
            return

        stripped = [line.strip() for line in self.output_buffer]
        self.output_buffer = []
        return stripped

    def read(self):
        """Pull line to end-of-file and store"""
        self.output_buffer.extend(self.file.readlines())
