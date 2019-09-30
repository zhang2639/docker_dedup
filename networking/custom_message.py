
class CustomMessage(object):

    def __init__(self, tag, body):
        self.tag = tag
        self.body = body

    def __str__(self):
        s = "Tag=%s #parts=%d: " % (self.tag, len(self.body))
        for p in self.body:
            s += "[%d: \"%s\"] " % (len(p), p if len(p) < 20 else "...")
        return s
