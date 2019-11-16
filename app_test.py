#!/usr/bin/env python
import eventlet
eventlet.monkey_patch()

import flask_cors
import json
from flask import Flask, render_template, request, Request, Response
from flask_socketio import SocketIO, disconnect
from threading import Event

async_mode = 'eventlet'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)


from collections import namedtuple


States = namedtuple('States', ('not_started', 'ended', 'playing', 'pause', 'buffering', 'cued'))

states = {
    -1: States.not_started,
    0: States.ended,
    1: States.playing,
    2: States.pause,
    3: States.buffering,
    5: States.cued
}


class Subject(object):
    def __init__(self):
        self._observers = []

    def register(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self, modifier=None):
        for observer in self._observers:
            if modifier != observer:
                observer.update(self)


class VideoStreamState(object):
    NAME = 'Unknown'
    RUNNING_STATES = (States.playing, )
    IDLE_STATES = (States.not_started, States.ended, States.buffering, States.pause, States.cued)

    def __init__(self, handler):
        self.timestamp = None
        self.handler = handler
        self.old_state = None

    def __str__(self):
        return self.NAME

    def process(self, video_state):
        if video_state in self.IDLE_STATES:
            self.handler.state = self.handler.idle_state
        elif video_state in self.RUNNING_STATES:
            self.handler.state = self.handler.running_state

    def get(self):
        return {
            'state': self.NAME,
            'timestamp': self.timestamp,
        }


class VideoStreamStateIdle(VideoStreamState):
    NAME = 'Idle'

    def __init__(self, handler):
        super(VideoStreamStateIdle, self).__init__(handler)


class VideoStreamStateRunning(VideoStreamState):
    NAME = 'Running'

    def __init__(self, handler):
        super(VideoStreamStateRunning, self).__init__(handler)


class VideoStreamHandler(object):
    def __init__(self, duration):
        self.duration = duration
        self.video_name = None
        self.idle_state = VideoStreamStateIdle(self)
        self.running_state = VideoStreamStateRunning(self)
        self.state = self.idle_state

    def update(self, data):
        print("data", data)
        current_time = data.get('current_time')
        video_state = states.get(data.get('current_state'))
        self.video_name = data.get('video_name')
        self.state.process(video_state)
        self.state.timestamp = current_time

    def get_state(self):
        return {
            'video_name': self.video_name,
            'duration': self.duration,
            'state': self.state.get()
        }


class VideoControler(Subject):
    def __init__(self):
        super(VideoControler, self).__init__()
        self.stream_handler = None

    def create_new(self, duration=0):
        self.stream_handler = VideoStreamHandler(duration)
        print("INITIAL BLET", self.get_state())

    def update(self, data):
        self.stream_handler.update(data)
        self.notify()

    def get_state(self):
        return self.stream_handler.get_state()


video_controller = VideoControler()


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@app.route('/api/video', methods=['POST'])
def create():
    video_controller.create_new(duration=request.json)
    return Response('', 200)


@app.route('/api/video_state', methods=['POST', 'GET'])
def video_handler():
    if request.method == 'POST':
        try:
            video_controller.update(request.json)
        except (AttributeError, TypeError):
            video_controller.create_new()
            return Response('Created new video', 200)

    return video_controller.get_state()


@socketio.on('disconnect')
def disconnect_handler():
    print("disconnect hooks")
    print("disconnect hooks ended")


@socketio.on('reboot')
def reboot():
    print("reboot called")
    disconnect()


if __name__ == '__main__':
    app.url_map.strict_slashes = False
    flask_cors.CORS(app, origins='*')
    socketio.run(app, host="0.0.0.0", port=2000)
