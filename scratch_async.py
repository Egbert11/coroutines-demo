#!/usr/bin/env python
# -*- coding: utf-8 -*-

# function: xxx
# author: jmhuang
# email: 946328371@qq.com
# date: 2018/10/6

# async
# - non-blocking sockets
# - callbacks
# - event loop


import socket
import time

try:
    import selectors
except ImportError:
    import selectors2 as selectors

selector = selectors.KqueueSelector()
n_task = 0


def get(path):
    global n_task
    n_task += 1
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    try:
        sock.connect(('localhost', 5000))
    except socket.error:
        pass
    callback = lambda: connected(sock, path)
    selector.register(sock.fileno(), selectors.EVENT_WRITE, data=callback)


def connected(sock, path):
    selector.unregister(sock.fileno())
    req = "GET %s HTTP/1.0\r\n\r\n" % path
    sock.send(req.encode())
    chunks = []
    callback = lambda: readable(sock, chunks)
    selector.register(sock.fileno(), selectors.EVENT_READ, data=callback)


def readable(sock, chunks):
    global n_task
    selector.unregister(sock.fileno())
    buf = sock.recv(1000)
    if buf:
        chunks.append(buf)
        callback = lambda: readable(sock, chunks)
        selector.register(sock.fileno(), selectors.EVENT_READ, data=callback)
    else:
        body = ''.join(chunks)
        print body.split('\n')[0]
        n_task -= 1


if __name__ == "__main__":
    start = time.time()
    get('/')
    get('/')
    get('/')
    while n_task:
        events = selector.select()
        for key, mask in events:
            cb = key.data
            cb()
    print "took %s" % (time.time() - start)