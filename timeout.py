import signal

# class to allow timeouts after a signal
class timeout:

	#constructor - takes number of seconds for how long
	# it should time out for
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message

    # handle the timeout with the given message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)

    # enter timeout
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    # exit timeout
    def __exit__(self, type, value, traceback):
        signal.alarm(0)