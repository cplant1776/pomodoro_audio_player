# Standard Library Imports
from time import strftime

# Third Party Imports

# Local Imports


class EventHandler:
    """Used by other classes to manage scheduling/canceling events"""
    def __init__(self):
        self.events = {}

    def schedule_event(self, event, event_name):
        """Schedules event to events dict with key event_name"""
        print("{} - Scheduled: {} ==> {}".format(strftime('%X'), event_name, event))
        self.events[event_name] = event

    def cancel_event(self, event_name):
        """Unschedules event in events dict with key event_name"""
        print("{} - Canceled: {} ==> {}".format(strftime('%X'), event_name, self.events[event_name]))
        self.events[event_name].cancel()
