import itertools
class StudySession:
    newid = itertools.count()

    def __init__(self, date, time, duration):
        self.date = date
        self.time = time
        self.duration = duration
        self.id = next(StudySession.newid)
        self.users = []