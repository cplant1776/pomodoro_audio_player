## Pomodoro Audio Assistant

A simple GUI-based Python program that handles music playback while practicing [the Pomodoro Technique® by Francesco Cirillo](https://en.wikipedia.org/wiki/Pomodoro_Technique). The program first lets the user set up their Pomodoro (how long is each work/rest interval, and how many). Next, the user selects audio sources to play during the different types of intervals (local playlist, [brain.fm](https://brain.fm/). Finally, the session screen will automatically shuffle the appropriate playlist for the interval and transition between intervals. The GUI is based on Kivy, so the app can be ported to Android and iPhone.

## Motivation

I created this project with two objectives:

1. Gain experience with working on a more complex project, as most of my experience had consisted of scripting or single-file applications.
2. Automate a process that I was already doing manually almost every day.
3. Learn the basics of GUI/event-driven programming, because I had never created something requiring a fleshed out GUI

This project began simply because one day I was using using the Pomodoro Technique® and got tired of manually switching the type of music I was listening to during the intervals. It began as a bare-bones script with no interface, but I figured it would be a good opportunity to advance my skills while building something I would actually use. Because I consistently make use of the program, I always have a stream of features I would like to add. This makes it easy to continue building on the project while learning more and more.

## Screenshots

Pomodoro session screen:

![Pomodoro session screen](screenshots/pomodoro_session.png?raw=true "Pomodoro session screen")

Selecting audio style:

![selecting source](screenshots/pomodoro_source.png?raw=true "selecting source")

Browsing local files:

![browsing for local playlist](screenshots/pomodoro_local_source.png?raw=true "browsing for local playlist")

## Current Features

* Select audio from two (2) sources: local playlist files, [brain.fm](https://brain.fm/)
* Automatically shuffles (non-repeating) playlist from appropriate playlist for each interval
* See both Pomodoro and Interval progress in real-time
* Pause/Resume interval progress
* Skip song or even the remainder of an interval

## Usage

#### Clone the Repo:
```shell
git clone https://github.com/cplant1776/pomodoro_audio_player
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

## Upcoming Changes/Fixes

* Merge Play/Resume buttons into a single toggle playback button
* Add a path for if user inputs invalid brain.fm credentials
* Add option to securely locally store user's Pomodoro preferences and credentials for easier login
* Add protections for if network connection drops during brain.fm session
* Explore viability of Spotify as a source
* General UI prettifying
