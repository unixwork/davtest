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

propfind_nstest1 = """<?xml version="1.0" encoding="UTF-8"?>
<x0:propfind xmlns:x0="DAV:">
    <x0:prop>
        <x1:getlastmodified xmlns:x1="DAV:" />
        <x2:getetag xmlns:x2="DAV:" />
    </x0:prop>
</x0:propfind>
"""

class TestXml(davtest.test.WebdavTest):
    def __init__(self):
        self.initialized = False

    def initTestData(self):
        if(self.initialized):
            return
        self.create_testdata('xml', 4)

    def test_xml_propfind_namespaces(self):
        self.initTestData()

        ms = assertMultistatusResponse(self.http.httpXmlRequest('PROPFIND', '/webdavtests/xml/res0', propfind_nstest1, 0), numResponses=1)
        for key, response in ms.response.items():
            lastmodified = response.get_property('DAV:', 'getlastmodified')
            etag = response.get_property('DAV:', 'getetag')

            assertProperty(response, 'DAV:', 'getlastmodified', status=200)
            assertProperty(response, 'DAV:', 'getetag', status=200)




