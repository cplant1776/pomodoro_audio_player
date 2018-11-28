from .timer import Timer
from .eventhandler import EventHandler


NUM_OF_WORK_INTERVALS = 4
NUM_OF_REST_INTERVALS = 3


class Session:
    def __init__(self):
        self.interval_duration = {'work': 10, 'rest': 5, 'long_rest': 15}

        self.playlist = {'work': None, 'rest': None}

        self.Intervals = {}
        self.interval_loop = 1

        self.Timer = Timer()
        self.EventHandler = EventHandler()

    def initialize_session_intervals(self):
        # Create all 8 intervals for the session (W-R-W-R-W-R-W-LR)
        self.Intervals.update(dict.fromkeys([1, 3, 5, 7], Interval(duration=self.interval_duration['work'],
                                                                   playlist=self.playlist['work'])))
        self.Intervals.update(dict.fromkeys([2, 4, 6], Interval(duration=self.interval_duration['rest'],
                                                                playlist=self.playlist['rest'])))
        self.Intervals[8] = Interval(duration=self.interval_duration['long_rest'],
                                     playlist=self.playlist['rest'])

        self.Timer.set_total_time(self.get_session_total_time())

    def start_next_interval(self):
        # Start interval
        self.Intervals[self.interval_loop].start()
        # Set event timer to length of interval
        self.Timer.set_event_duration(self.Intervals[self.interval_loop].duration)
        # Reset event time passed
        self.Timer.reset_event_time_passed()
        # Star session timer
        self.Timer.start()

        # Schedule event to end current interval
        end_interval_event = Clock.schedule_once(self.end_interval,
                                                 self.Timer.event_duration)
        self.EventHandler.schedule_event(event=end_interval_event, event_name='end_interval')

    def end_interval(self, *args):
        print("{} - Execute: {}".format(strftime('%X'), "end_interval"))

        self.Intervals[self.interval_loop].stop()
        # Pause session timer
        self.Timer.pause()

        # If final interval, end the session
        if self.interval_loop == 8:
            self.end_session()
        else:
            self.interval_loop += 1

        print("Start Interval " + str(self.interval_loop))

        self.start_next_interval()

    def skip_interval(self):
        # Unschedule current end event
        self.EventHandler.cancel_event(event_name='end_interval')
        # Unschedule current session progression
        self.Timer.pause()
        # Update time remaining in session w/ remaining interval time
        self.Timer.update_time_passed_since_start()

        self.end_interval()
        print("end interval")

    def pause_interval(self):
        # Unschedule current end event
        self.EventHandler.cancel_event(event_name='end_interval')
        # Unschedule current session progression
        self.Timer.pause()
        # Pause current song
        self.Intervals[self.interval_loop].pause()

    def resume_interval(self):
        # Start song
        self.Intervals[self.interval_loop].resume()

        # Reschedule interval transition
        end_interval_event = Clock.schedule_once(self.end_interval, self.Timer.get_event_time_remaining())
        print("INTERVAL TIME REMAINING: {}".format(self.Timer.get_event_time_remaining()))
        self.EventHandler.schedule_event(event=end_interval_event, event_name='end_interval')

        # Reschedule session progress event
        self.Timer.start()
        print("RESUME INTERVAL")

    def end_session(self):
        print("SESSION END")
        quit()

    def get_session_total_time(self):
        return (self.interval_duration['work'] * NUM_OF_WORK_INTERVALS +
                self.interval_duration['rest'] * NUM_OF_REST_INTERVALS +
                self.interval_duration['long_rest'])