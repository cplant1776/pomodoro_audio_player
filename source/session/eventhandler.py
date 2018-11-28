from time import strftime


class EventHandler:
    def __init__(self):
        self.events = {}

    def schedule_event(self, event, event_name):
        print("{} - Scheduled: {}".format(strftime('%X'), event_name))
        self.events[event_name] = event

    def cancel_event(self, event_name):
        print("{} - Canceled: {}".format(strftime('%X'), event_name))
        self.events[event_name].cancel()