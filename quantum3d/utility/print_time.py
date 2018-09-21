import time


class Time:
    """
    Initialize object to start the timer for print 
    use Time.read() to read the elapsed time from the start time 
    at the end use Time.stop() to stop the timer and read the hole time elapsed 
    """

    def __init__(self):
        self.start_time = time.time()

    def restart(self):
        self.start_time = time.time()

    # return value as milliseconds (SECONDS?!)
    def read(self):
        elapsed_time = time.time() - self.start_time
        return int(elapsed_time)

    def stop(self):
        elapsed_time = time.time() - self.start_time
        self.start_time = None
        return int(elapsed_time)
