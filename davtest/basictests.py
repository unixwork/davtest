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
import sys

from xml.dom import minidom
from davtest.connection import Http, concatPath

propfind = """<?xml version="1.0" encoding="UTF-8"?>
<D:propfind xmlns:D="DAV:">
    <D:prop>
        <D:creationdate/>
        <D:getetag/>
        <D:resourcetype/>
    </D:prop>
</D:propfind>
"""

def basic_tests(http):
    # PROPFIND test
    # check if result is 207
    # and do some basic xml checks

    conn = http.xmlRequest('PROPFIND', '/', propfind, '1')
    res = conn.getresponse()
    data = res.read()
    if res.status != 207:
        print('PROPFIND failed', file=sys.stderr)
        print('status code = %d, 207 expected' % res.status, file=sys.stderr)
        print('response:', file=sys.stderr)
        print(data.decode('ascii'), file=sys.stderr)
        return False
    # xml checks
    try:
        doc = minidom.parseString(data)
    except:
        print('PROPFIND xml error', file=sys.stderr)
        print('response:', file=sys.stderr)
        print(data.decode('ascii'), file=sys.stderr)
        return False

    # root element should be multistatus
    if doc.documentElement.localName != 'multistatus':
        print('PROPFIND xml error', file=sys.stderr)
        print('root element must be "multistatus"', file=sys.stderr)
        return False
    elms = doc.documentElement.getElementsByTagNameNS('DAV:', 'response')
    if len(elms) < 1:
        print('PROPFIND xml error', file=sys.stderr)
        print('missing "response" element', file=sys.stderr)
        print(data.decode('ascii'), file=sys.stderr)
        return False
    r1 = elms[0]
    r1href = r1.getElementsByTagNameNS('DAV:', 'href')
    r1propstat = r1.getElementsByTagNameNS('DAV:', 'propstat')
    if len(r1href) < 1 or len(r1propstat) < 1:
        print('failed', file=sys.stderr)
        print('incomplete response element', file=sys.stderr)
        print(data.decode('ascii'), file=sys.stderr)
        return False
    # end of PROPFIND tests

    # MKCOL test
    # check if result is 2xx
    conn = http.simpleRequest('DELETE', '/testcol/') # make sure /testcol doesn't exists
    res = conn.getresponse()

    conn = http.simpleRequest('MKCOL', '/testcol/')
    res = conn.getresponse()
    data = res.read()
    if not (200 <= res.status <= 299):
        print('MKCOL failed', file=sys.stderr)
        print('status code = %d, 2xx expected' % res.status, file=sys.stderr)
        print(data.decode('ascii'), file=sys.stderr)
        return False

    # create test collection for other tests
    conn = http.simpleRequest('DELETE', '/webdavtests/')  # make sure /webdavtests doesn't exists
    res = conn.getresponse()

    conn = http.simpleRequest('MKCOL', '/webdavtests/')
    res = conn.getresponse()
    if not (200 <= res.status <= 299):
        print('MKCOL failed', file=sys.stderr)
        print('cannot create "webdavtests/", status = %d' % res.status, file=sys.stderr)
        print(data, file=sys.stderr)
        return False
    conn = http.xmlRequest('PROPFIND', '/webdavtests/', propfind, '0')
    res = conn.getresponse()
    if res.status != 207:
        print('PROPFIND failed', file=sys.stderr)
        print('cannot access "webdavtests/", status = %d' % res.status, file=sys.stderr)

    # end of MKCOL tests

    # DELETE test
    # check if resource is deleted by performing PROPFIND for the same URL
    conn = http.simpleRequest('DELETE', '/testcol/')
    res = conn.getresponse()
    data = res.read()
    if not (200 <= res.status <= 299):
        print('DELETE failed', file=sys.stderr)
        print('status code = %d, 2xx expected' % res.status, file=sys.stderr)
        print(data.decode('ascii'), file=sys.stderr)
        return False
    # is is possible that DELETE failed but returned a 207 multistatus response
    # we don't check that or parse the result
    # check if DELETE was successful by doing a PROPFIND request for /testcol
    conn = http.xmlRequest('PROPFIND', '/testcol', propfind, '1')
    res = conn.getresponse()
    if res.status != 404:
        print('DELETE not successful, PROPFIND status = %d, 404 expected' % res.status, file=sys.stderr)
        print(data.decode('ascii'), file=sys.stderr)
        return False
    # end of DELETE tests

    # PUT test
    # upload new resource and check status code
    # check content of uploaded resource with GET
    testcontent = 'Hello World'
    conn = http.simpleRequest('PUT', '/basictestres1', testcontent)
    res = conn.getresponse()
    data = res.read()
    if not (200 <= res.status <= 299):
        print('PUT failed', file=sys.stderr)
        print('status code = %d, 2xx expected' % res.status, file=sys.stderr)
        print(data.decode('ascii'), file=sys.stderr)
        return False

    conn = http.simpleRequest('GET', '/basictestres1')
    res = conn.getresponse()
    data = res.read()
    if res.status != 200:
        print('GET failed', file=sys.stderr)
        print('GET status code = %d, 200 expected' % res.status, file=sys.stderr)
        print(data.decode('ascii'), file=sys.stderr)
        return False
    if data.decode('ascii') != testcontent:
        print('GET failed', file=sys.stderr)
        print('wrong content, "%s" expected' % testcontent, file=sys.stderr)
        print(data.decode('ascii'), file=sys.stderr)
        return False

    conn = http.simpleRequest('DELETE', '/basictestres1')
    res = conn.getresponse()
    if not (200 <= res.status <= 299):
        print('failed', file=sys.stderr)
        print('cannot delete basictestres1, status = %' % res.status, file=sys.stderr)
        return False

    # end of PUT tests
    print('basic tests passed', file=sys.stderr)
    return True


