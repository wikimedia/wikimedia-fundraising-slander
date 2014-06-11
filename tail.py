class TailPoller(object):
    """Tail -f a file as the message source"""

    def __init__(self, path=None):
        print "Initializing file tailer on: [{path}]".format(path=path)

        self.path = path
        self.file = file(path, "r")

        # fast-forward to the end-of-file
        self.file.seek(0, 2)

    def check(self):
        return [l.strip() for l in self.file.readlines()]
