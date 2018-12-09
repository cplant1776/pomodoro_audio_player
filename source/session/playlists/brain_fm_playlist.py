from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import TimeoutException

from time import sleep
from os import environ

# @pQ2U5V@#N4Wz1OBAJ
BRAIN_FM_URL = "https://brain.fm/login"


class BrainFMPlaylist:
    def __init__(self, browser):
        self.browser = browser
        self.current_mode = 'work'

    def start(self):
        self.browser.start_focus()

    def stop(self):
        self.browser.toggle_playback()

    def pause(self):
        self.browser.toggle_playback()

    def resume(self):
        self.browser.toggle_playback()

    def skip_track(self):
        pass

    def toggle_mode(self):
        self.browser.toggle_current_mode(self.current_mode)
        if self.current_mode == 'work':
            self.current_mode = 'rest'
        else:
            self.current_mode = 'work'


class BrainFMBrowser:
    def __init__(self, username='', password=''):
        self.url = BRAIN_FM_URL
        # Pull credentials from environmental variables
        # self.username = environ['BRAIN_FM_EMAIL']
        # self.password = environ['BRAIN_FM_PASSWORD']
        self.username = username
        self.password = password
        self.driver = self.create_headless_driver()

        self.css_selectors = {'home': '[href="/app"] > div',
                              'focus': '[class*="focus"]',
                              'focus_time': ['div[class^=modules-music-player-css-DurationH]'],
                              'relax': '[class*="relax"]',
                              'relax_style': 'div[class*="optionContainer"]:nth-child(2)',
                              'relax_duration': 'div[class="timeOptionNumber"]',
                              'playback_toggle': '[class*="PlayControl"]'}

        self.log_in()

    @staticmethod
    def create_headless_driver():
        options = Options()
        # Set browser to headless mode
        # options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        return driver

    def toggle_current_mode(self, current_mode=''):
        self.navigate_to_home()
        if current_mode == 'rest':
            self.start_focus()
        else:
            self.start_relax()

    def log_in(self):
        # Load the page
        self.driver.get(self.url)
        # Fill out credentials
        self.enter_login_credentials()
        # Submit credentials
        self.protected_click(self.driver.find_element_by_id("login-confirm-btn"))

        # Wait for page to load
        self.wait_for_page_load(delay=10, selector='[class*="focus"]')

    def enter_login_credentials(self):
        # Find form inputs
        user_email_input = self.driver.find_element_by_id("login-email")
        user_password_input = self.driver.find_element_by_id("login-password")
        # Fill out form
        user_email_input.send_keys(self.username)
        user_password_input.send_keys(self.password)

    def click_and_wait_for_load(self, button_selector='', wait_selector='', index=None):
        if index:
            button = self.driver.find_element_by_css_selector(button_selector)[index]
        else:
            button = self.driver.find_element_by_css_selector(button_selector)
        self.protected_click(button)
        self.wait_for_page_load(selector=wait_selector)

    def start_focus(self):
        self.click_and_wait_for_load(button_selector=self.css_selectors['focus'],
                                     wait_selector=self.css_selectors['focus_time'])
        # focus_button = self.driver.find_element_by_css_selector('[class*="focus"]')
        # self.protected_click(focus_button)
        # self.wait_for_page_load(selector='[class*="focus"]')

    def start_relax(self):
        # Choose relax
        self.click_and_wait_for_load(button_selector=self.css_selectors['relax'],
                                     wait_selector=self.css_selectors['relax_style'])
        # relax_button = self.driver.find_element_by_css_selector('[class*="relax"]')
        # self.protected_click(relax_button)
        # self.wait_for_page_load(selector='[class*="relax"]')
        # Set to relax mode
        # relax_style_button = self.driver.find_element_by_css_selector('div[class*="optionContainer"]:nth-child(2)')
        # self.protected_click(relax_style_button)
        self.click_and_wait_for_load(button_selector=self.css_selectors['relax_style'],
                                     wait_selector=self.css_selectors['relax_duration'])
        # Choose relaxation duration
        self.click_and_wait_for_load(button_selector=self.css_selectors['relax_duration'],
                                     wait_selector=self.css_selectors['playback_toggle'],
                                     index=1)
        # relax_duration_button = self.driver.find_elements_by_css_selector('div[class="timeOptionNumber"]')
        # self.protected_click(relax_duration_button[1])

    def set_duration_to_infinite(self):
        # Set duration to infinite
        infinity_button = self.driver.find_element_by_xpath('//button[text()="2 hours"]/following-sibling::button')
        self.protected_click(infinity_button)

    def skip_track(self):
        skip_button = self.driver.find_element_by_xpath('//a[text()="Skip >>"]')
        self.protected_click(skip_button)

    def navigate_to_home(self):
        home_button = self.driver.find_element_by_css_selector('[href="/app"] > div')
        self.protected_click(home_button)
        self.wait_for_page_load(selector='[class*="focus"]')

    def toggle_playback(self):
        play_control_button = self.driver.find_element_by_css_selector('[class*="PlayControl"]')
        self.protected_click(play_control_button)

    def wait_for_page_load(self, delay=10, selector=''):
        try:
            found_element = WebDriverWait(self.driver, delay).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
        finally:
            print("Page ready!")
            return True

    def protected_click(self, button):
        try:
            button.click()
        except ElementNotInteractableException:
            print("Button not found!")
