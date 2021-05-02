class TestDuration(object):
    def __init__(self, start_time: int, end_time: int):
        self.start_time = start_time
        self.end_time = end_time

    def __str__(self):
        return str(self.__dict__)
