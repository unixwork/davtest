import http.client
import logging


def capture_http(*args):
    pass
    #print(args)

def setup_logging():
    http.client.HTTPConnection.debuglevel = 1
    http.client.HTTPSConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    http.client.print = capture_http
