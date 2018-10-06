#!/usr/bin/env python
# -*- coding: utf-8 -*-

# function: xxx
# author: jmhuang
# email: 946328371@qq.com
# date: 2018/10/6

# coroutines
# - Future
# - generator
# - Task


import socket
import time

try:
    import selectors
except ImportError:
    import selectors2 as selectors

selector = selectors.KqueueSelector()
n_task = 0


class Future(object):
    def __init__(self):
        self.callbacks = []

    def resolve(self):
        for cb in self.callbacks:
            cb()


class Task(object):
    def __init__(self, gen):
        self.gen = gen
        self.step()

    def step(self):
        try:
            fut = next(self.gen)
        except StopIteration:
            return
        fut.callbacks.append(self.step)


def get(path):
    global n_task
    n_task += 1
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    try:
        sock.connect(('localhost', 5000))
    except socket.error:
        pass

    f = Future()
    selector.register(sock.fileno(), selectors.EVENT_WRITE, data=f)
    yield f
    # sock is writable!!!
    selector.unregister(sock.fileno())

    req = "GET %s HTTP/1.0\r\n\r\n" % path
    sock.send(req.encode())
    chunks = []
    while True:
        f = Future()
        selector.register(sock.fileno(), selectors.EVENT_READ, data=f)
        yield f
        selector.unregister(sock.fileno())

        buf = sock.recv(1000)
        if buf:
            chunks.append(buf)
        else:
            body = ''.join(chunks)
            print body.split('\n')[0]
            n_task -= 1
            return


if __name__ == "__main__":
    start = time.time()
    Task(get('/'))
    Task(get('/'))
    Task(get('/'))
    while n_task:
        events = selector.select()
        for key, mask in events:
            fut = key.data
            fut.resolve()
    print "took %s" % (time.time() - start)