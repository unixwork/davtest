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

ns = "https://unixwork.de/davtest/"

proppatch1 = """<?xml version="1.0" encoding="utf-8" ?>
<D:propertyupdate xmlns:D="DAV:">
    <D:set>
        <D:prop>
            <D:myprop>testvalue1</D:myprop>
        </D:prop>
    </D:set>
</D:propertyupdate>
"""

proppatch2 = """<?xml version="1.0" encoding="utf-8" ?>
<D:propertyupdate xmlns:D="DAV:">
    <D:set>
        <D:prop>
            <Z:myprop xmlns:Z="https://unixwork.de/davtest/">testvalue1</Z:myprop>
        </D:prop>
    </D:set>
</D:propertyupdate>
"""

proppatch3_remove = """<?xml version="1.0" encoding="utf-8" ?>
<D:propertyupdate xmlns:D="DAV:">
    <D:remove>
        <D:prop>
            <Z:myprop xmlns:Z="https://unixwork.de/davtest/" />
        </D:prop>
    </D:remove>
</D:propertyupdate>
"""

propfind_z_myprop = """<?xml version="1.0" encoding="UTF-8"?>
<D:propfind xmlns:D="DAV:">
    <D:prop>
        <Z:myprop xmlns:Z="https://unixwork.de/davtest/"/>
    </D:prop>
</D:propfind>
"""


class TestProppatch(davtest.test.WebdavTest):
    def test_proppatch_set_response(self):
        self.create_testdata('proppatch_set1', 1)

        res = self.http.httpXmlRequest('PROPPATCH', '/webdavtests/proppatch_set1/res0', proppatch1)
        if res.status != 207:
            raise Exception(f'wrong status code: {res.status}')

        if len(res.body) == 0:
            raise Exception(f'no proppatch response body')

        ms = davtest.webdav.Multistatus(res.body)
        if len(ms.response) != 1:
            raise Exception(f'wrong number of response elements')

        response = next(iter(ms.response.values()))
        prop = response.get_property('DAV:', 'myprop')
        errprop = response.get_property('DAV:', 'myprop')

        if prop is None and errprop is None:
            raise Exception('missing property in response')

    def test_proppatch_set_deadproperty(self):
        self.create_testdata('proppatch_set2', 1)

        res = self.http.httpXmlRequest('PROPPATCH', '/webdavtests/proppatch_set2/res0', proppatch2)
        if res.status != 207:
            raise Exception(f'wrong status code: {res.status}')

        if len(res.body) == 0:
            raise Exception(f'no proppatch response body')

        ms = davtest.webdav.Multistatus(res.body)
        if len(ms.response) != 1:
            raise Exception(f'wrong number of response elements')

        response = next(iter(ms.response.values()))
        prop = response.get_property(ns, 'myprop')

        if prop is None:
            raise Exception('missing property in response')

        if prop.status != 200:
            raise Exception('wrong property status code')

        res = self.http.httpXmlRequest('PROPFIND', '/webdavtests/proppatch_set2/res0', propfind_z_myprop, 0)
        if res.status != 207:
            raise Exception(f'propfind: wrong status code: {res.status}')

        if len(res.body) == 0:
            raise Exception(f'no propfind response body')

        ms = davtest.webdav.Multistatus(res.body)
        if len(ms.response) != 1:
            raise Exception(f'wrong number of response elements in propfind request')

        response = next(iter(ms.response.values()))
        prop = response.get_property(ns, 'myprop')

        if prop is None:
            raise Exception('missing property in propfind response')

        content = davtest.webdav.getElmContent(prop.elm)
        if content is None:
            raise Exception('missing property content')

        if str(content) != 'testvalue1':
            raise Exception('wrong property content')

    def test_proppatch_remove_deadproperty(self):
        self.create_testdata('proppatch_remove1', 1)

        res = self.http.httpXmlRequest('PROPPATCH', '/webdavtests/proppatch_remove1/res0', proppatch2)
        ms = davtest.webdav.Multistatus(res.body)
        response = next(iter(ms.response.values()))
        prop = response.get_property(ns, 'myprop')

        if prop is None:
            raise Exception('missing property in response')
        if prop.status != 200:
            raise Exception('wrong property status code')

        # test remove
        res = self.http.httpXmlRequest('PROPPATCH', '/webdavtests/proppatch_remove1/res0', proppatch3_remove)
        if res.status != 207:
            raise Exception(f'proppatch remove: wrong status code: {res.status}')

        ms = davtest.webdav.Multistatus(res.body)
        if len(ms.response) != 1:
            raise Exception(f'wrong number of response elements in proppatch request')

        response = next(iter(ms.response.values()))
        prop = response.get_property(ns, 'myprop')
        if prop.status != 200:
            raise Exception('prop remove: wrong status code')

        # check with propfind, if the resource was deleted
        res = self.http.httpXmlRequest('PROPFIND', '/webdavtests/proppatch_remove1/res0', propfind_z_myprop, 0)
        if res.status != 207:
            raise Exception(f'propfind: wrong status code: {res.status}')

        if len(res.body) == 0:
            raise Exception(f'no propfind response body')

        ms = davtest.webdav.Multistatus(res.body)
        if len(ms.response) != 1:
            raise Exception(f'wrong number of response elements in propfind request')

        response = next(iter(ms.response.values()))
        propfind_prop = response.get_err_property(ns, 'myprop')
        if propfind_prop is None:
            raise Exception('no error prop')
        if propfind_prop.status != 404:
            raise Exception('property not removed')
