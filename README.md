## Pomodoro Audio Assistant

A simple GUI-based Python program that handles music playback while practicing [the Pomodoro Technique® by Francesco Cirillo](https://en.wikipedia.org/wiki/Pomodoro_Technique). The program first lets the user set up their Pomodoro (how long is each work/rest interval, and how many). Next, the user selects audio sources to play during the different types of intervals (local playlist, [brain.fm](https://brain.fm/), and spotify playlist). Finally, the session screen will automatically shuffle the appropriate playlist for the interval and transition between intervals. The GUI is based on Kivy, so the app can be ported to Android and iPhone.

## Motivation

1. Gain experience with working on a more complex project, as most of my previous experience had consisted of scripting or single-file applications.
2. Automate a process that I was already doing manually almost every day.
3. Learn the basics of GUI/event-driven programming, because I had never created something requiring a fleshed out GUI

This project began simply because one day I was using using the Pomodoro Technique® and got tired of manually switching the type of music I was listening to during the intervals. It began as a bare-bones script with no interface, but I figured it would be a good opportunity to advance my skills while building something I would actually use.

## In Action

![Starting a Spotify session](docs/screenshots/gif_01.gif?raw=true "Starting a Spotify session")

![Playback page](docs/screenshots/gif_02.gif?raw=true "Playback page")

![browsing for local playlist](docs/screenshots/pomodoro_local_source.png?/raw=true "browsing for local playlist")

## Current Features

* Select audio from two (3) sources: local playlist files, [brain.fm](https://brain.fm/), or Spotify
* Automatically shuffles (non-repeating) playlist from appropriate playlist for each interval
* See both Pomodoro and Interval progress in real-time
* Pause/Resume interval progress
* Skip song or even the remainder of an interval

## Usage

#### Clone the Repo:
```shell
git clone https://github.com/cplant1776/pomodoro_audio_player.git
```
#### Running

Note that You may need to substitute "python3" below for the appropriate command on your system.

```shell
python3 main.py
```
The UI is quite basic and self explanatory.

#### Requirements

##### Python
```
version 3.X
```
##### Packages

```
See requirements.txt
```

##### Browser

```
Mozilla Firefox
or
Google Chrome
```

##### Webdriver

To use Brain.fm or Spotify as a source, you will need either Mozilla Firefox or Google Chrome and its accompanying webdriver. [More info here.](https://selenium-python.readthedocs.io/installation.html#drivers) You can find links to the drivers below:

* [Mozilla Firefox - geckodriver](https://github.com/mozilla/geckodriver/releases)
* [Google Chrome - ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads)

## To-Do

* Handle mid-session network drops
* Add ability to securely store user's preferences and credentials