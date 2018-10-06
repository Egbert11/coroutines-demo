#!/usr/bin/env python
# -*- coding: utf-8 -*-

# function: xxx
# author: jmhuang
# email: 946328371@qq.com
# date: 2018/10/6

import time
from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    time.sleep(1)
    return "Hello everyone!\nNice to meet you!"

try:
    app.run('0.0.0.0', 5000, debug=True)
except KeyboardInterrupt:
    pass