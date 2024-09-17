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
        <D:getlastmodified/>
        <D:creationdate/>
        <D:getetag/>
        <D:resourcetype/>
    </D:prop>
</D:propfind>
"""

propfind2_404 = """<?xml version="1.0" encoding="UTF-8"?>
<D:propfind xmlns:D="DAV:">
    <D:prop>
        <D:getlastmodified/>
        <D:creationdate/>
        <D:getetag/>
        <D:resourcetype/>
        <D:nonexistingproperty/>
    </D:prop>
</D:propfind>
"""

class TestPropfind(davtest.test.WebdavTest):
    def create_testdata(self, colname, num_res):
        path = f'/webdavtests/{colname}/'
        res = self.http.doRequest('MKCOL', path)
        if res.status != 201:
            raise Exception(f'cannot create test collection: {res.status}')

        for i in range(num_res):
            res_path = f'{path}res{i}'
            res = self.http.doRequest('PUT', res_path, f'testcontent {i}')
            if res.status > 299:
                raise Exception(f'cannot create test resource {1}: {res.status}')

    def test_propfind_depth0(self):
        # create some test data
        #
        # /propfind_depth0/
        # /propfind_depth0/res1
        self.create_testdata('propfind_depth0', 1)

        # do tests
        for path in ('/webdavtests/propfind_depth0/', '/webdavtests/propfind_depth0', '/webdavtests/propfind_depth0/res0'):
            res = self.http.httpXmlRequest('PROPFIND', path, propfind1, 0)
            if res.status != 207:
                raise Exception(f'path: {path} : wrong status code: {res.status}')

            if len(res.body) == 0:
                raise Exception(f'path: {path} : no propfind response body')

            ms = davtest.webdav.Multistatus(res.body)
            if len(ms.response) != 1:
                raise Exception(f'path: {path} : wrong number of response elements')

    def test_propfind_depth1(self):
        # create some test data
        #
        # /propfind_depth1/
        # /propfind_depth1/res1
        # /propfind_depth1/res2
        # /propfind_depth1/res3
        self.create_testdata('propfind_depth1', 3)

        # do tests
        res = self.http.httpXmlRequest('PROPFIND', '/webdavtests/propfind_depth1', propfind1, 1)
        if res.status != 207:
            raise Exception(f'wrong status code: {res.status}')

        if len(res.body) == 0:
            raise Exception(f'no propfind response body')

        ms = davtest.webdav.Multistatus(res.body)
        if len(ms.response) < 4:
            raise Exception(f'wrong number of response elements')

    def test_property_status(self):
        self.create_testdata('propfind_status', 1)

        # do tests
        res = self.http.httpXmlRequest('PROPFIND', '/webdavtests/propfind_status', propfind2_404, 1)
        if res.status != 207:
            raise Exception(f'wrong status code: {res.status}')

        if len(res.body) == 0:
            raise Exception(f'no propfind response body')

        ms = davtest.webdav.Multistatus(res.body)
        for key, response in ms.response.items():
            lastmodified = response.get_property('DAV:', 'getlastmodified')
            if lastmodified is None:
                raise Exception('no getlastmodified property element')

            if lastmodified.status != 200:
                raise Exception(f'wrong getlastmodified status code: {lastmodified.status}')

            nonexistingproperty = response.get_err_property('DAV:', 'nonexistingproperty')
            if nonexistingproperty is None:
                raise Exception('no nonexistingproperty property element')

            if nonexistingproperty.status != 404:
                raise Exception(f'wrong nonexistingproperty status code: {lastmodified.status}')

    def test_resource_type(self):
        self.create_testdata('propfind_resourcetype', 1)

        # do tests
        # check if a collection resource has a resourcetype element
        # that contains a DAV:collection element

        res = self.http.httpXmlRequest('PROPFIND', '/webdavtests/propfind_resourcetype', propfind1, 0)
        if res.status != 207:
            raise Exception(f'wrong status code: {res.status}')

        if len(res.body) == 0:
            raise Exception(f'no propfind response body')

        ms = davtest.webdav.Multistatus(res.body)
        for key, collection in ms.response.items():
            # only one element: the propfind_resourcetype collection
            resource_type = collection.get_property('DAV:', 'resourcetype')

            if resource_type is None:
                raise Exception('no resourcetype property')

            if resource_type.status > 299:
                raise Exception(f'wrong resourcetype status code: {resource_type.status}')

            elm = resource_type.elm
            iscollection = False
            collection_node = davtest.webdav.getElms(elm, 'DAV:', 'collection')
            if collection_node is None:
                raise Exception('missing <DAV:collection> element')
