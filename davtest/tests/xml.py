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
from parted import freeAllDevices

import davtest.test
import davtest.webdav

from davtest.webdav import assertMultistatusResponse
from davtest.webdav import assertProperty

ns = "https://unixwork.de/davtest/"
ns1 = "https://unixwork.de/davtest/ns1"

propfind_nstest1 = """<?xml version="1.0" encoding="UTF-8"?>
<x0:propfind xmlns:x0="DAV:">
    <x0:prop>
        <x1:getlastmodified xmlns:x1="DAV:" />
        <x2:getetag xmlns:x2="DAV:" />
    </x0:prop>
</x0:propfind>
"""

proppatch_elmdecl1 = """<?xml version="1.0" encoding="utf-8" ?>
<D:propertyupdate xmlns:D="DAV:">
    <D:set>
        <D:prop>
            <z:myprop xmlns:z="https://unixwork.de/davtest/"><z:elm1/><z:elm2/></z:myprop>
        </D:prop>
    </D:set>
</D:propertyupdate>
"""

proppatch_globaldecl1 = """<?xml version="1.0" encoding="utf-8" ?>
<D:propertyupdate xmlns:D="DAV:" xmlns:z="https://unixwork.de/davtest/">
    <D:set>
        <D:prop>
            <z:myprop><z:elm1/><z:elm2/></z:myprop>
        </D:prop>
    </D:set>
</D:propertyupdate>
"""
proppatch_mixdecl1 = """<?xml version="1.0" encoding="utf-8" ?>
<D:propertyupdate xmlns:D="DAV:" xmlns:z="https://unixwork.de/davtest/ns1">
    <D:set>
        <D:prop>
            <a:myprop xmlns:a="https://unixwork.de/davtest/"><z:elm1/><z:elm2/></a:myprop>
        </D:prop>
    </D:set>
</D:propertyupdate>
"""


test1_propfind = """<?xml version="1.0" encoding="UTF-8"?>
<D:propfind xmlns:D="DAV:">
    <D:prop>
        <x0:myprop xmlns:x0="https://unixwork.de/davtest/" />
    </D:prop>
</D:propfind>
"""

class TestXml(davtest.test.WebdavTest):
    def __init__(self):
        self.initialized = False

    def test_xml_propfind_namespaces(self):
        self.create_testdata('xml0', 1)

        ms = assertMultistatusResponse(self.http.httpXmlRequest('PROPFIND', '/webdavtests/xml0/res0', propfind_nstest1, 0), numResponses=1)
        for key, response in ms.response.items():
            lastmodified = response.get_property('DAV:', 'getlastmodified')
            etag = response.get_property('DAV:', 'getetag')

            assertProperty(response, 'DAV:', 'getlastmodified', status=200)
            assertProperty(response, 'DAV:', 'getetag', status=200)

    def test_xml_proppatch_elmdecl(self):
        self.create_testdata('xml1', 1)

        ms = assertMultistatusResponse(
            self.http.httpXmlRequest('PROPPATCH', '/webdavtests/xml1/res0', proppatch_elmdecl1), numResponses=1)
        assertProperty(ms.get_first_response(), ns, 'myprop', status=200)

        ms = assertMultistatusResponse(
            self.http.httpXmlRequest('PROPFIND', '/webdavtests/xml1/res0', test1_propfind, 0),
            numResponses=1)
        assertProperty(ms.get_first_response(), ns, 'myprop', status=200)

        # check property content
        response = ms.get_first_response()
        myprop = response.get_property(ns, 'myprop')
        for elm in myprop.elm.childNodes:
            if elm.nodeType == elm.ELEMENT_NODE:
                if elm.namespaceURI != ns:
                    raise Exception('wrong namespace in property children')


    def test_xml_proppatch_globaldecl(self):
        self.create_testdata('xml2', 1)

        ms = assertMultistatusResponse(
            self.http.httpXmlRequest('PROPPATCH', '/webdavtests/xml2/res0', proppatch_globaldecl1), numResponses=1)
        assertProperty(ms.get_first_response(), ns, 'myprop', status=200)

        ms = assertMultistatusResponse(
            self.http.httpXmlRequest('PROPFIND', '/webdavtests/xml2/res0', test1_propfind, 0),
            numResponses=1)
        assertProperty(ms.get_first_response(), ns, 'myprop', status=200)

        # check property content
        response = ms.get_first_response()
        myprop = response.get_property(ns, 'myprop')
        for elm in myprop.elm.childNodes:
            if elm.nodeType == elm.ELEMENT_NODE:
                if elm.namespaceURI != ns:
                    raise Exception('wrong namespace in property children')

    def test_xml_mixdecl(self):
        self.create_testdata('xml3', 1)

        ms = assertMultistatusResponse(
            self.http.httpXmlRequest('PROPPATCH', '/webdavtests/xml3/res0', proppatch_mixdecl1), numResponses=1)
        assertProperty(ms.get_first_response(), ns, 'myprop', status=200)

        ms = assertMultistatusResponse(
            self.http.httpXmlRequest('PROPFIND', '/webdavtests/xml3/res0', test1_propfind, 0),
            numResponses=1)
        assertProperty(ms.get_first_response(), ns, 'myprop', status=200)

        # check property content
        response = ms.get_first_response()
        myprop = response.get_property(ns, 'myprop')
        for elm in myprop.elm.childNodes:
            if elm.nodeType == elm.ELEMENT_NODE:
                if elm.namespaceURI != ns1:
                    raise Exception('wrong namespace in property children')

