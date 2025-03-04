import http.client
import logging
import codecs

request_buf = ""
response_buf = ""

def capture_http(*args):
    global request_buf
    global response_buf
    unescaped = codecs.decode(args[1], 'unicode_escape')
    if args[0] == 'send:':
        send = unescaped[2:-1]
        lines = send.splitlines()
        #request_buf += send
        for line in lines:
            if not line.lower().startswith('authorization'):
                request_buf += line + '\n'
    elif args[0] == 'reply:':
        response_buf += unescaped[1:-1]
    else:
        response_buf += args[1] + args[2] + '\r\n'


def setup_logging():
    http.client.HTTPConnection.debuglevel = 1
    http.client.HTTPSConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    http.client.print = capture_http

def get_request_data():
    global request_buf
    global response_buf
    req = (request_buf, response_buf)
    request_buf = ""
    response_buf = ""
    return req
