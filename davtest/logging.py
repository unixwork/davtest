import http.client
import logging

request_buf = ""
response_buf = ""

def capture_http(*args):
    global request_buf
    global response_buf
    if args[0] == 'send:':
        request_buf += args[1]
    elif args[0] == 'reply:':
        response_buf += args[1]
    else:
        response_buf += args[1] + '\r\n'


def setup_logging():
    http.client.HTTPConnection.debuglevel = 1
    http.client.HTTPSConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    http.client.print = capture_http

def get_request_data():
    global request_buf
    global response_buf
    req = (request_buf, request_buf)
    request_buf = ""
    response_buf = ""
    return req
