# -*- encoding: utf-8 -*-
import time

from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    time.sleep(1.3)
    return 'Hello, World!'

