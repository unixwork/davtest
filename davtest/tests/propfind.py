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


import davtest.test
import davtest.webdav

propfind1 = """<?xml version="1.0" encoding="UTF-8"?>
<D:propfind xmlns:D="DAV:">
    <D:prop>
        <D:creationdate/>
        <D:getetag/>
        <D:resourcetype/>
    </D:prop>
</D:propfind>
"""

class TestPropfind(davtest.test.WebdavTest):
    def test_propfind_depth0(self):
        # create some test data
        #
        # /propfind_depth0/
        # /propfind_depth0/res1

        res = self.http.doRequest('MKCOL', '/webdavtests/propfind_depth0/')
        if res.status != 201:
            raise Exception(f'cannot create test collection: {res.status}')

        res = self.http.doRequest('PUT', '/webdavtests/propfind_depth0/res1', 'testcontent 1')
        if res.status > 299:
            raise Exception(f'cannot create test resource 1: {res.status}')

        # do tests
        for path in ('/webdavtests/propfind_depth0/', '/webdavtests/propfind_depth0', '/webdavtests/propfind_depth0/res1'):
            res = self.http.httpXmlRequest('PROPFIND', path, propfind1, 0)
            if res.status != 207:
                raise Exception(f'path: {path} : wrong status code: {res.status}')

            if len(res.body) == 0:
                raise Exception(f'path: {path} : no propfind response body')

            ms = davtest.webdav.Multistatus(res.body)
            if len(ms.response) != 1:
                raise Exception(f'path: {path} : wrong number of response elements')




