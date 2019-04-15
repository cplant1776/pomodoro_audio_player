# Standard Library Imports
import os
import time


# Third Party Imports
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, ElementClickInterceptedException, WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import url_contains
import spotipy
from spotipy import oauth2


# Local Imports
from source.functions import create_headless_driver


# =========================
# CONSTANTS
# =========================
PUBLIC_CLIENT_ID = 'fda8d241ac5f41d18df47391d853accb'
PUBLIC_CLIENT_SECRET = '3c30c5317e5a4b9398f599a26e9ac428'
SPOTIFY_SCOPE = "streaming user-read-birthdate user-read-email user-read-private user-modify-playback-state user-read-playback-state"
REDIRECT_URI = 'http://localhost/'
CSS_SELECTORS = {'username': '#login-username',
                 'password': '#login-password',
                 'login_button': '#login-button'}


class SpotifyAuthenticator:
    """Gets an authentication token from the Spotify Authentication API"""

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.auth_token = None

    def generate_authentication_token(self, scope=SPOTIFY_SCOPE, client_id=PUBLIC_CLIENT_ID,
                                      client_secret=PUBLIC_CLIENT_SECRET, redirect_uri=REDIRECT_URI, cache_path=None):
        """
            modified version of spotipy's util.prompt_for_user_token. This makes it headless.

            returns the user token suitable for use with the spotipy.Spotify
            constructor

            Parameters:
             - username - the Spotify username
             - scope - the desired scope of the request
             - client_id - the client id of the app
             - client_secret - the client secret of the app
             - redirect_uri - the redirect URI of the app
             - cache_path - path to save tokens to
        """
        if not client_id:
            client_id = os.getenv('SPOTIPY_CLIENT_ID')

        if not client_secret:
            client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')

        if not redirect_uri:
            redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')

        if not client_id:
            print('''
                You need to set your Spotify API credentials. You can do this by
                setting environment variables like so:
                export SPOTIPY_CLIENT_ID='your-spotify-client-id'
                export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
                export SPOTIPY_REDIRECT_URI='your-app-redirect-url'
                Get your credentials at     
                    https://developer.spotify.com/my-applications
            ''')
            raise spotipy.SpotifyException(550, -1, 'no credentials set')

        cache_path = cache_path or ".cache-" + self.username
        sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri,
                                       scope=scope, cache_path=cache_path)

        # try to get a valid token for this user, from the cache,
        # if not in the cache, the create a new

        token_info = sp_oauth.get_cached_token()

        if not token_info:
            print('''
                User authentication requires interaction with your
                web browser. Once you enter your credentials and
                give authorization, you will be redirected to
                a url.  Paste that url you were directed to to
                complete the authorization.
            ''')
            auth_url = sp_oauth.get_authorize_url()

            # driver = create_headless_driver()
            driver = webdriver.Chrome()
            driver.get(auth_url)

            fill_credentials(driver, self.username, self.password)
            try:
                submit_credentials(driver)
            except WebDriverException:
                print("Submit credentials failed!")

            print("Opened %s in your browser" % auth_url)

            try:
                WebDriverWait(driver, 10).until(url_contains("http://localhost/?code="))
                response = driver.current_url
            except:
                print("Never redirected to token!")
                return None

            code = sp_oauth.parse_response_code(response)
            token_info = sp_oauth.get_access_token(code)

        # Auth'ed API request
        if token_info:
            self.auth_token = token_info['access_token']
            return True
        else:
            return None

    def update_credentials(self, username='', password=''):
        self.username = username
        self.password = password


def fill_credentials(driver, username, password):
    """Fills in username/password fields in login form"""
    # Find form inputs
    username_input = driver.find_element_by_css_selector(CSS_SELECTORS['username'])
    password_input = driver.find_element_by_css_selector(CSS_SELECTORS['password'])
    # Clear previous input if present
    username_input.send_keys(Keys.BACKSPACE * 100)
    password_input.send_keys(Keys.BACKSPACE * 100)
    # Fill out form
    username_input.send_keys(username)
    password_input.send_keys(password)


def submit_credentials(driver):
    button = driver.find_element_by_css_selector(CSS_SELECTORS['login_button'])
    protected_click(button)


def protected_click(button):
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
        time.sleep(0.5)
        protected_click(button)
