# Standard Library Imports
from math import isclose
from threading import Thread

# Third Party Imports
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.bubble import Bubble
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar

# Local Imports
from source.functions import download_temporary_image, get_temp_file_path


class ScrollableLabel(ScrollView):
    text = StringProperty('')


class SessionScreenProgressBar(ProgressBar):
    progress_max = NumericProperty(None)
    progress_value = NumericProperty(None)


class ConnectingLabel(Label):
    angle = NumericProperty(0)
    startCount = NumericProperty(-1)
    count = NumericProperty(0)

    def __init__(self, **kwargs):
        super(ConnectingLabel, self).__init__(**kwargs)
        self.count = self.startCount
        self.animation_event = None
        # self.angle = 0

    def start_animation(self):
        self.animation_event = Clock.schedule_interval(self.set_circle, 1.0/360)

    def stop_animation(self):
        if self.animation_event:
            self.animation_event.cancel()

    def set_circle(self, dt):
        self.angle = self.angle + dt*360
        if self.angle >= 360:
            self.angle = 0


class SessionScreenButton(Button):
    def on_release(self):
        self.parent.parent.parent.parent.suspend_buttons()


class FailedSubmissionPopup(ModalView):
    def __init__(self, message, **kwargs):
        super(ModalView, self).__init__(**kwargs)
        self.ids.failed_submission_label.text = message + "\nAre you sure you wish to continue?"


class UniversalHelpPopup(ModalView):
    def __init__(self, display_text, **kwargs):
        super(ModalView, self).__init__(**kwargs)
        self.ids.help_label.text = display_text
        # Hide black background
        self.background_color = (0, 0, 0, 0)
        # Make invisible
        self.opacity = 0

    def fade_in_help_pop(self):
        self.fade_tick_event = Clock.schedule_interval(self.fade_tick, 1 / 50)

    def fade_tick(self, *args):
        if isclose(self.opacity, 1, abs_tol=10**-2):
            self.fade_tick_event.cancel()
        else:
            self.opacity += 1/15


class StartScreenRow(BoxLayout):
    out_value = NumericProperty(0)
    initial_value = NumericProperty(0)
    display_text = StringProperty('')
    slider_max = NumericProperty(60)


class StartScreenTextInput(TextInput):
    def __init__(self, **kwargs):
        super(StartScreenTextInput, self).__init__(**kwargs)

    def validate_text(self, root):
        if int(self.text) < root.slider_max + 1:
            self.text = self.text and self.text[:2]
            # StartScreen function
            root.parent.parent.hide_textinput_error_label()
        else:
            self.text = str(root.initial_value)
            # StartScreen function
            root.parent.parent.show_textinput_error_label()
        root.out_value = int(self.text)


class SelectedSpotifyPlaylistBox(BoxLayout):
    display_title = StringProperty('')
    selected_playlist_img_path = StringProperty('./assets/images/blank.png')
    selected_playlist_name = StringProperty('')
    selected_playlist_uri = StringProperty('')

    def __init__(self, **kwargs):
        super(SelectedSpotifyPlaylistBox, self).__init__(**kwargs)

    def draw_playlist_label_background(self):
        label = self.ids['playlist_name']
        with label.canvas.before:
            Color(0/255, 140/255, 145/255, 1)
            label.rect = RoundedRectangle(pos=label.pos,
                                         size=label.size,
                                         radius=[10, ])


class SearchResultsView(ScrollView):
    text = StringProperty('')

    def __init__(self, **kwargs):
        super(SearchResultsView, self).__init__(**kwargs)
        self.thumbnails = []
        self.rows = []
        self.download_threads = []

    def populate_thumbnails(self, results):
        # Remove any thumbnails from a previous search
        self.clear_previous_results()
        # Get args to pass to thumbnails
        thumbnail_info = self.get_thumbnail_info(results=results)
        # Start downloading images
        self.download_images(thumbnail_info)
        # Wait for download finish
        for thread in self.download_threads:
            thread.join()
        # Generate thumbnails
        self.generate_thumbnail_objects(args=thumbnail_info)
        # Add thumbnails to screen
        for thumbnail in self.thumbnails:
            self.ids.content_box.add_widget(thumbnail)

    def download_images(self, thumbnail_info):
        del self.download_threads[:]
        # Download all images simultaneously
        for entry in thumbnail_info:
            self.download_threads.append(Thread(target=download_temporary_image,
                                                args=(entry['img_url'], entry['img_path'])))
            self.download_threads[-1].start()

    def clear_previous_results(self):
        if self.thumbnails:
            # Empty previous lists
            del self.thumbnails[:]
            del self.rows[:]
            # Remove rows from scrollview
            self.ids.content_box.clear_widgets()

    def generate_thumbnail_objects(self, args):
        # Generate thumbnail object for each entry
        for entry in args:
            self.thumbnails.append(SearchResultsThumbnail(img_path=entry['img_path'],
                                                          playlist_name=entry['playlist_name'],
                                                          playlist_uri=entry['playlist_uri']))

    def clear_current_selection(self):
        for thumbnail in self.ids.content_box.children:
            if hasattr(thumbnail, 'rect'):
                thumbnail.canvas.before.remove(thumbnail.rect)
                del thumbnail.rect

    def get_thumbnail_info(self, results):
        thumbnail_args = []
        for entry in results['playlists']['items']:
            entry_info = {}
            # Get playlist name and url
            entry_info['playlist_name'] = entry['name']
            entry_info['playlist_uri'] = entry['uri']
            # Generate image path from url name and get it
            entry_info['img_url'] = entry['images'][0]['url']
            entry_info['img_path'] = get_temp_file_path(entry_info['img_url'])
            # Add thumbnail info to result
            thumbnail_args.append(entry_info)

        return thumbnail_args


class SearchResultsThumbnail(ButtonBehavior, BoxLayout):
    img_path = StringProperty('')
    playlist_name = StringProperty('')
    playlist_uri = StringProperty('')

    def __init__(self, **kwargs):
        super(SearchResultsThumbnail, self).__init__(**kwargs)

    def draw_select(self):
        with self.canvas.before:
            Color(0/255, 140/255, 145/255, 1)
            self.rect = Rectangle(pos=self.pos, size=(self.width, self.height))
