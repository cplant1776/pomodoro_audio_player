# Standard Library Imports
from itertools import cycle
from os import environ
from time import sleep

# Third Party Imports
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, ElementClickInterceptedException, ElementNotVisibleException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


# Local Imports
from source.functions import create_headless_driver, update_current_playback_info_brainfm
from source.session.playlists.playlist import Playlist


# =========================
# CONSTANTS
# =========================
MODE_TOGGLE = cycle(['work', 'rest'])
BRAIN_FM_URL = "https://brain.fm/login"
CSS_SELECTORS = {'home_button'          : '[href="/app"] > div',
                 'focus'                : '[class*="focus"]',
                 'focus_time'           : 'button[class^=modules-music-player-css-DurationOption__wrapper]',
                 'relax'                : '[class*="relax"]',
                 'relax_style'          : 'div[class*="optionContainer"]:nth-child(2)',
                 'relax_duration'       : 'div[class="timeOptionNumber"]',
                 'playback_toggle'      : '[class*="PlayControl"]',
                 'login_user'           : '#login-email',
                 'login_pw'             : '#login-password',
                 'login_button'         : '#login-confirm-btn',
                 'skip_track_button'    : '[class*="Skip"]',
                 'invalid_credentials': '.Toastify__progress-bar--error'
                 }


def alternate_mode():
    """Returns alternating value each time it'c called: swaps between 'work' and 'rest'"""
    return next(MODE_TOGGLE)


class BrainFMPlaylist(Playlist):
    """Container for BrainFMBrowser"""
    def __init__(self, browser):
        super().__init__()
        self.browser = browser
        self.current_mode = 'rest'

    def start(self, style=""):
        self.toggle_mode()

    def stop(self):
        self.browser.toggle_playback()

    def pause(self):
        self.browser.toggle_playback()

    def resume(self):
        self.browser.toggle_playback()

    def skip_track(self):
        self.browser.click_skip_button()

    def toggle_mode(self):
        """Swaps browser between rest/work modes"""
        self.current_mode = alternate_mode()
        self.browser.set_current_mode(self.current_mode)
        update_current_playback_info_brainfm()


class BrainFMBrowser:
    """Selenium driver that navigates https://brain.fm/"""
    def __init__(self, username='', password=''):
        if username == '' and password == '':
            # Pull credentials from environmental variables
            self.username = environ['BRAIN_FM_EMAIL'].strip('"')
            self.password = environ['BRAIN_FM_PASSWORD'].strip('"')
        else:
            self.username, self.password = username, password
        # self.driver = webdriver.Chrome()
        self.driver = create_headless_driver()
        self.driver.get(BRAIN_FM_URL)

    def set_current_mode(self, current_mode=None):
        """Navigate to work/rest page"""
        self.navigate_to_home()
        self.start_focus() if current_mode == 'work' else self.start_relax()

    def try_login(self):
        self.enter_login_credentials()

        # Click submit and watch for invalid credentials popup for 3 sec
        error_found = self.click_and_wait_for_load(button_selector=CSS_SELECTORS['login_button'],
                                     wait_selector=CSS_SELECTORS['invalid_credentials'],
                                     delay=3)
        print("error found: {}".format(error_found))
        if error_found:
            return False
        else:
            return True

    def enter_login_credentials(self):
        """Fills in username/password fields in login form"""
        # Find form inputs
        user_email_input = self.driver.find_element_by_css_selector(CSS_SELECTORS['login_user'])
        user_password_input = self.driver.find_element_by_css_selector(CSS_SELECTORS['login_pw'])
        # Clear previous input if exists
        user_email_input.send_keys(Keys.BACKSPACE * 100)
        user_password_input.send_keys(Keys.BACKSPACE * 100)
        # Fill out form
        user_email_input.send_keys(self.username)
        user_password_input.send_keys(self.password)

    def click_and_wait_for_load(self, button_selector='', wait_selector='', delay=10):
        """Clicks an element based on button_selector and waits for full load before continuing"""
        print('Clicked: {} Waiting for: {}'.format(button_selector, wait_selector))
        button = self.driver.find_element_by_css_selector(button_selector)
        self.protected_click(button)
        was_found = self.wait_for_page_load(delay=delay, selector=wait_selector)
        return was_found

    def start_focus(self):
        """Navigates to page that plays focus audio"""
        print('start_focus')
        self.click_and_wait_for_load(button_selector=CSS_SELECTORS['focus'],
                                     wait_selector=CSS_SELECTORS['focus_time'])

    def start_relax(self):
        """Navigates to page that plays relax audio"""
        # Choose relax
        print('start_relax')
        self.click_and_wait_for_load(button_selector=CSS_SELECTORS['relax'],
                                     wait_selector=CSS_SELECTORS['relax_style'])

        self.click_and_wait_for_load(button_selector=CSS_SELECTORS['relax_style'],
                                     wait_selector=CSS_SELECTORS['relax_duration'])
        # Choose relaxation duration
        self.click_and_wait_for_load(button_selector=CSS_SELECTORS['relax_duration'],
                                     wait_selector=CSS_SELECTORS['playback_toggle'])

    def click_skip_button(self):
        """Skips currently playing track and plays next"""
        skip_button = self.driver.find_element_by_css_selector(CSS_SELECTORS['skip_track_button'])
        self.protected_click(skip_button)

    def navigate_to_home(self):
        """Nagivates to home page of site"""
        print('navigate_to_home')
        self.click_and_wait_for_load(button_selector=CSS_SELECTORS['home_button'],
                                     wait_selector=CSS_SELECTORS['focus'])

    def toggle_playback(self):
        """Clicks play/pause button"""
        print('toggle_playback')
        play_control_button = self.driver.find_element_by_css_selector(CSS_SELECTORS['playback_toggle'])
        self.protected_click(play_control_button)

    def wait_for_page_load(self, delay=10, selector=''):
        """Returns True once selector finds element, or times out after delay seconds"""
        print('wait_for_page_load')
        try:
            found_element = WebDriverWait(self.driver, delay).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, str(selector)))
            )
        except TimeoutException:
            print("Timed out!")
            return False

        print("Page ready!")
        return True

    def protected_click(self, button):
        """Attempts to click an element

        Exceptions:
        ElementNotInteractableException - button not found
        ElementClickInterceptedException - element hidden behind something. Wait and try again

        """
        try:
            button.click()
        except ElementNotInteractableException:
            print("Button not found!")
        except ElementClickInterceptedException:
            sleep(0.5)
            self.protected_click(button)
        except StaleElementReferenceException:
            return
        except ElementNotVisibleException:
            return

    def update_credentials(self, username='', password=''):
        self.username = username
        self.password = password


class InvalidCredentials(Exception):
    pass
