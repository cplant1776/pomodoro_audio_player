# Standard Library Imports

# Third Party Imports
from kivy.clock import Clock

# Local Imports

class Timer:
    """Handles timing for events"""
    def __init__(self):
        self.total_time = 0
        self.time_passed_since_start = 0

        self.event_duration = 0
        self.event_time_passed = 0

        self.time_passed_update_event = None

    def set_total_time(self, total_time=0):
        self.total_time = total_time

    def set_event_duration(self, event_duration=0):
        self.event_duration = event_duration

    def reset_event_time_passed(self):
        self.event_time_passed = 0

    def start(self):
        """Start tick event that fires every 1 second"""
        self.time_passed_update_event = Clock.schedule_interval(self.update_time_passed, 1)

    def pause(self):
        """Cancel tick event"""
        self.time_passed_update_event.cancel()

    def update_time_passed(self, *args):
        """Increment total time and event time passed by 1 sec"""
        self.time_passed_since_start += 1
        self.event_time_passed += 1
        print("{}: {}".format(self, self.event_time_passed))

    def get_event_time_passed(self):
        return self.event_time_passed

    def update_time_passed_since_start(self):
        """Updates total time when skipping an event (such as an interval or track)"""
        self.time_passed_since_start += self.event_duration - self.event_time_passed

    def get_event_time_remaining(self):
        """Returns seconds remaining in the current event"""
        print("="*20 + "\n" + "EVENT DURATION: {}\nEVENT TIME PASSED: {}\n".format(self.event_duration, self.event_time_passed) + "="*20)
        return self.event_duration - self.event_time_passed
