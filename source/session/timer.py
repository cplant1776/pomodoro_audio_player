from kivy.clock import Clock


class Timer:
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
        self.time_passed_update_event = Clock.schedule_interval(self.update_time_passed, 1)

    def pause(self):
        self.time_passed_update_event.cancel()

    def update_time_passed(self, *args):
        self.time_passed_since_start += 1
        self.event_time_passed += 1
        print("{}: {}".format(self, self.event_time_passed))

    def get_event_time_passed(self):
        return self.event_time_passed

    def update_time_passed_since_start(self):
        self.time_passed_since_start += self.event_duration - self.event_time_passed

    def get_event_time_remaining(self):
        print("="*20 + "\n" + "EVENT DURATION: {}\nEVENT TIME PASSED: {}\n".format(self.event_duration, self.event_time_passed) + "="*20)
        return self.event_duration - self.event_time_passed
