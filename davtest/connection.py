#
# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS HEADER.
#
# Copyright 2024 Olaf Wintermann. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   1. Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#   2. Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

from base64 import b64encode
from urllib.parse import urlparse
import http.client

class HttpResponse:
    def __init__(self, status, header, body):
        self.status = status
        self.headers = header
        self.body = body

class Http:
    def __init__(self, config):
        self.config = config
        self.basicauth = 'Basic ' + b64encode(str.encode(config['user'] + ':' + config['password'])).decode('ascii')

        # get host and path from url
        url = urlparse(config['url'])

        # make surewe have an http or https url
        if url.scheme != 'http' and url.scheme != 'https':
            print('Error: url scheme must be http or https')
            print('Abort.')
            exit(1)

        self.scheme = url.scheme
        self.host = url.netloc
        self.path = url.path or '/'

    def getpath(self, p):
        return concatPath(self.path, p)

    # return conn, hdr
    def connection(self, path):
        if self.scheme == 'https':
            conn = http.client.HTTPSConnection(self.host)
        else:
            conn = http.client.HTTPConnection(self.host)

        hdr = {'Authorization': self.basicauth}
        return conn, hdr

    # return conn
    def xmlRequest(self, method, path, xml, depth=None, ctype='application/xml', hdrs=()):
        urlPath = path if path.startswith('http://') or path.startswith('https://') else concatPath(self.path, path)

        conn, hdr = self.connection(urlPath)
        if depth is not None:
            hdr.update({'Depth': depth})

        for h in hdrs:
            hdr.update(h)

        hdr.update({'Content-Type': ctype})

        conn.request(method, urlPath, xml, hdr)

        return conn

    # return HttpResponse
    def httpXmlRequest(self, method, path, xml, depth=None, ctype='application/xml', hdrs=(), retry=0):
        if retry > 10:
            raise Exception('xmlRequestResponse: too many requests')

        conn = self.xmlRequest(method, path, xml, depth, ctype, hdrs)

        response = conn.getresponse()
        if response.status == 301 or response.status == 302:
            location = response.getheader('Location')
            return self.httpXmlRequest(method, location, xml, depth, ctype, hdrs, retry+1)

        return HttpResponse(response.status, response.headers, response.read())


    # return conn
    def simpleRequest(self, method, path, content = None):
        urlPath = path if path.startswith('http://') or path.startswith('https://') else concatPath(self.path, path)

        conn, hdr = self.connection(urlPath)
        if content is None:
            conn.request(method, urlPath, headers=hdr)
        else:
            conn.request(method, urlPath, content, hdr)

        return conn

    # return HttpResponse
    def doRequest(self, method, path, content = None, retry = 0):
        if retry > 10:
            raise Exception('request: too many requests')

        conn = self.simpleRequest(method, path, content)
        response = conn.getresponse()
        if response.status == 301 or response.status == 302:
            location = response.getheader('Location')
            return self.doRequest(method, location, content, retry + 1)

        return HttpResponse(response.status, response.headers, response.read())

    def mkcol(self, path):
        urlPath = concatPath(self.path, path)
        conn, hdr = self.connection(urlPath)
        conn.request('MKCOL', urlPath, headers=hdr)
        res = conn.getresponse()
        if not (200 <= res.status <= 299):
            print('failed, MKCOL %s : status = %d' % (urlPath, res.status))
            return False
        return True

    def put(self, path, content):
        urlPath = concatPath(self.path, path)
        conn, hdr = self.connection(urlPath)
        conn.request('PUT', urlPath, content, hdr)
        res = conn.getresponse()
        if not (200 <= res.status <= 299):
            print('failed, PUT %s : status = %d' % (urlPath, res.status))
            return False
        return True



# utility function that concats two path segments
def concatPath(a, b):
    if a[-1:] == '/':
        a = a[:-1]
    if b[0:1] == '/':
        b = b[1:]
    return a + '/' + b
