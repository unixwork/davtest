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

import http.client
import xml.dom
from urllib.parse import urlparse

get_resource_req = """<?xml version="1.0" encoding="UTF-8"?>
<D:propfind xmlns:D="DAV:">
    <D:prop>
        <D:displayname/>
        <D:lastmodified/>
        <D:creationdate/>
        <D:getetag/>
        <D:resourcetype/>
    </D:prop>
</D:propfind>
"""

def getElms(elm, ns, name):
    return [e for e in elm.childNodes if e.nodeType == e.ELEMENT_NODE and e.namespaceURI == ns and e.localName == name]

def getElmContent(elm):
    return elm.childNodes[0].data

def elmKey(elm):
    return '{' + elm.namespaceURI + '} : {' + elm.localName + '}'

def propKey(ns, name):
    return '{' + ns + '} : {' + name + '}'

def get_status(statusStr):
    s = statusStr.split()
    if len(s) == 3:
        return int(s[1])
    return 500

class Prop:
    def __init__(self, elm, status):
        self.ns = elm.namespaceURI
        self.name = elm.localName
        self.status = status
        self.elm = elm

class Response:
    def __init__(self, href):
        self.href = href
        self.properties = {}
        self.error_properties = {}

    def add_property(self, elm, status):
        key = elmKey(elm)
        prop = Prop(elm, status)

        if status >= 200 and status <= 299:
            self.properties[key] = prop
        else:
            self.error_properties[key] = prop

    def get_property(self, ns, name):
        key = propKey(ns, name)
        return self.properties.get(key)



class Multistatus:
    def __init__(self, multistatusStr):
        self.doc = xml.dom.minidom.parseString(multistatusStr)
        self.response = {}
        self.parse()


    def parse(self):
        elms = self.doc.documentElement.getElementsByTagNameNS('DAV:', 'response')
        for elm in elms:
            href = getElms(elm, 'DAV:', 'href')
            if len(href) != 1:
                raise Exception('multistatus: href elm count != 1')
            href_str = getElmContent(href[0])

            # if href is a full url, extract the path
            if href_str.startswith('http://') or href_str.startswith('https://'):
                url = urlparse(href_str)
                href_str = url.path

            # remove trailing '/'
            if len(href_str) > 0 and href_str[-1] == '/':
                href_str = href_str[:-1]

            response = Response(href_str)
            self.response.update({response.href: response})

            propstat = getElms(elm, 'DAV:', 'propstat')
            for ps in propstat:
                statusElms = getElms(ps, 'DAV:', 'status')
                statusNum = 500
                if len(statusElms) == 1:
                    statusStr = getElmContent(statusElms[0])
                    statusNum = get_status(statusStr)

                propElms = getElms(ps, 'DAV:', 'prop')
                for propElm in propElms:
                    props = propElm.childNodes
                    for prop in props:
                        if prop.nodeType == prop.ELEMENT_NODE:
                            response.add_property(prop, statusNum)




def resource_exists(http, path):
    res = http.httpXmlRequest('PROPFIND', path, get_resource_req, '0')
    if res.status != 207:
        return False

    ms = Multistatus(res.body)
    # there should be exactly one response, however the path
    # could be different
    if len(ms.response) == 1:
        return True

    return False