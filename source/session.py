from kivy.core.audio import SoundLoader
from random import shuffle
from kivy.clock import Clock

from time import sleep, strftime


NUM_OF_WORK_INTERVALS = 4
NUM_OF_REST_INTERVALS = 3


class Session:
    def __init__(self):
        self.interval_duration = {'work': 3, 'rest': 2, 'long_rest': 5}

        self.playlist = {'work': [], 'rest': []}

        self.Intervals = {}
        self.interval_loop = 1

        self.Timer = Timer()
        self.EventHandler = EventHandler()


    @staticmethod
    def get_songs_string(playlist):
        # extract every other entry (the file name)
        return ''.join(playlist[0::2])

    @staticmethod
    def get_path_list(playlist):
        # get list of song directories in random order
        result = playlist[1::2]
        shuffle(result)
        return result

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
        self.Intervals[self.interval_loop].start()
        self.Timer.set_event_duration(self.Intervals[self.interval_loop].duration)
        self.Timer.start()

        end_interval_event = Clock.schedule_once(self.end_interval,
                                                 self.Timer.event_duration)
        self.EventHandler.schedule_event(event=end_interval_event, event_name='end_interval')

    def end_interval(self, *args):

        self.Intervals[self.interval_loop].stop()
        self.Timer.pause()

        if self.interval_loop == 8:
            self.end_session()
        else:
            self.interval_loop += 1

        self.start_next_interval()

        print("Start Interval " + str(self.interval_loop))

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
        # Save interval position for resume
        print("pause_interval")

    def resume_interval(self):
        # Start song
        self.Intervals[self.interval_loop].resume()

        # Reschedule interval transition
        end_interval_event = Clock.schedule_once(self.end_interval, self.Timer.get_event_time_remaining())
        self.EventHandler.schedule_event(event=end_interval_event, event_name='end_interval')

        # Reschedule session progress event
        self.Timer.start()
        print("start_interval")

    def end_session(self):
        print(self.interval_loop)
        quit()

    def get_session_total_time(self):
        return int(self.interval_duration['work'] * NUM_OF_WORK_INTERVALS +
                   self.interval_duration['rest'] * NUM_OF_REST_INTERVALS +
                   self.interval_duration['long_rest'])


class Interval:
    def __init__(self, duration=0, playlist=[]):

        self.playlists = {'current': None, 'full': playlist}
        # current playlist gets popped until it is empty, then refills
        self.refill_current_playlist()

        self.songs = {'current': Song(), 'next': Song()}

        self.duration = duration

        self.Timer = Timer()
        self.EventHandler = EventHandler()

    def start(self):
        # Pop 1st song into current_playlist and start playing it
        self.set_next_song()
        self.play_next_song()

    def set_next_song(self):
        self.songs['next'] = Song(path=self.pop_song_path_from_playlist())

    def pop_song_path_from_playlist(self):
        popped_song = self.playlists['current'].pop()
        # If current_playlist is empty, refill it
        if not self.playlists['current']:
            self.refill_current_playlist()
        return popped_song

    def refill_current_playlist(self):
        self.playlists['current'] = [i for i in self.playlists['full']]

    def play_current_song(self):
        self.songs['current'].play()

    def queue_next_song(self):
        self.songs['current'], self.songs['next'] = self.songs['next'], Song(self.pop_song_path_from_playlist())
        self.songs['current'].load()

    def set_current_song_event_length(self):
        self.Timer.reset_event_time_passed()
        self.Timer.set_event_duration(self.songs['current'].get_length())

    def play_next_song(self):
        # Change next-song to current-song and pop a new next-song
        self.queue_next_song()

    #     start song
        self.play_current_song()
        self.set_current_song_event_length()
        self.Timer.start()

    #     set up play_next_song to trigger after current song duration
    #     print("*" * 20,"\n",int(self.songs['current'].get_length()),"\n","*" * 20)
        end_song_event = Clock.schedule_once(self.end_current_song,
                                             int(self.songs['current'].get_length()))
        self.EventHandler.schedule_event(event=end_song_event, event_name='end_song')

    def end_current_song(self, *args):
        self.songs['current'].stop()
        self.Timer.pause()
        self.play_next_song()

    def pause_song(self):
        # Unschedule event to transition to next song
        # self.EventHandler.cancel_event(event_name='end_song')
        # Stop playing
        self.songs['current'].stop()
        # Stop timer
        self.Timer.pause()

        print("Pause song")

    def resume_song(self):
        # Reload song and start playing
        self.play_current_song()
        self.Timer.start()
        # Jump to pause position
        self.songs['current'].seek(self.Timer.event_time_passed)
        # Schedule event to transition to next song
        end_song_event = Clock.schedule_once(self.end_current_song,
                                             self.Timer.get_event_time_remaining())
        self.EventHandler.schedule_event(event=end_song_event, event_name='end_song')

        # Reset seek position
        print("resume song")

    def pause(self):
        self.pause_song()

    def resume(self):
        self.resume_song()

    def stop(self):
        # self.EventHandler.cancel_event('end_song')
        self.songs['current'].stop()


class Song:
    def __init__(self, path=None):
        self.path = path
        self.song = None

        self.time_elapsed = 0
        self.time_remaining = 0

    def load(self):
        self.song = SoundLoader.load(self.path)

    def play(self):
        self.song.play()

    def stop(self):
        self.song.stop()

    def seek(self, position):
        self.song.seek(position)

    def get_length(self):
        return self.song.length


class EventHandler:
    def __init__(self):
        self.events = {}

    def schedule_event(self, event, event_name):
        print("{} - Scheduled: {}".format(strftime('%X'), event_name))
        self.events[event_name] = event

    def cancel_event(self, event_name):
        print("{} - Canceled: {}".format(strftime('%X'), event_name))
        self.events[event_name].cancel()


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
        print("{}: {}".format(self,self.event_time_passed))

    def get_event_time_passed(self):
        return self.event_time_passed

    def update_time_passed_since_start(self):
        self.time_passed_since_start += int(self.event_duration - self.event_time_passed)

    def get_event_time_remaining(self):
        return int(self.event_duration - self.event_time_passed)






