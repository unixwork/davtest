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

from davtest.webdav import assertMultistatusResponse
from davtest.webdav import assertProperty

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

proppatch4_fail1 = """<?xml version="1.0" encoding="utf-8" ?>
<D:propertyupdate xmlns:D="DAV:">
    <D:set>
        <D:prop>
            <Z:myprop xmlns:Z="https://unixwork.de/davtest/">testvalue1</Z:myprop>
            <D:getetag>newetag</D:getetag><!-- illegal -->
        </D:prop>
    </D:set>
</D:propertyupdate>
"""

proppatch5_rm_unknown = """<?xml version="1.0" encoding="utf-8" ?>
<D:propertyupdate xmlns:D="DAV:">
    <D:remove>
        <D:prop>
            <Z:unknown_prop xmlns:Z="https://unixwork.de/davtest/" />
        </D:prop>
    </D:remove>
</D:propertyupdate>
"""

proppatch5_rm_unknown_set = """<?xml version="1.0" encoding="utf-8" ?>
<D:propertyupdate xmlns:D="DAV:">
    <D:remove>
        <D:prop>
            <Z:unknown_prop xmlns:Z="https://unixwork.de/davtest/" />
        </D:prop>
    </D:remove>
    <D:set>
        <D:prop>
            <Z:myprop xmlns:Z="https://unixwork.de/davtest/">testvalue1</Z:myprop>
        </D:prop>
    </D:set>
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

        ms = assertMultistatusResponse(self.http.httpXmlRequest('PROPPATCH', '/webdavtests/proppatch_set1/res0', proppatch1), numResponses=1)

        response = ms.get_first_response()
        prop = response.get_property('DAV:', 'myprop')
        errprop = response.get_property('DAV:', 'myprop')

        if prop is None and errprop is None:
            raise Exception('missing property in response')

    def test_proppatch_set_deadproperty(self):
        self.create_testdata('proppatch_set2', 1)

        ms = assertMultistatusResponse(self.http.httpXmlRequest('PROPPATCH', '/webdavtests/proppatch_set2/res0', proppatch2), numResponses=1)

        assertProperty(ms.get_first_response(), ns, 'myprop', status=200)

        ms = assertMultistatusResponse(self.http.httpXmlRequest('PROPFIND', '/webdavtests/proppatch_set2/res0', propfind_z_myprop, 0), numResponses=1)
        assertProperty(ms.get_first_response(), ns, 'myprop', content='testvalue1', status=200)

    def test_proppatch_remove_deadproperty(self):
        self.create_testdata('proppatch_remove1', 1)

        ms = assertMultistatusResponse(self.http.httpXmlRequest('PROPPATCH', '/webdavtests/proppatch_remove1/res0', proppatch2))
        assertProperty(ms.get_first_response(), ns, 'myprop', status=200)

        # test remove
        ms = assertMultistatusResponse(self.http.httpXmlRequest('PROPPATCH', '/webdavtests/proppatch_remove1/res0', proppatch3_remove), numResponses=1)
        assertProperty(ms.get_first_response(), ns, 'myprop', status=200)

        # check with propfind, if the resource was deleted
        ms = assertMultistatusResponse(self.http.httpXmlRequest('PROPFIND', '/webdavtests/proppatch_remove1/res0', propfind_z_myprop, 0), numResponses=1)
        assertProperty(ms.get_first_response(), ns, 'myprop', status=404)

    def test_proppatch_failed_dependency(self):
        self.create_testdata('proppatch_fail1', 1)

        ms = assertMultistatusResponse(self.http.httpXmlRequest('PROPPATCH', '/webdavtests/proppatch_fail1/res0', proppatch4_fail1), numResponses=1)
        response = ms.get_first_response()
        myprop = response.get_err_property(ns, 'myprop')
        failprop = response.get_err_property('DAV:', 'getetag')

        if myprop is None or failprop is None:
            raise Exception('expected failed property')

        if myprop.status != 424:
            raise Exception('wrong status code for failed dependency')

    def test_proppatch_remove_unknown_prop(self):
        self.create_testdata('proppatch_rm_unknown', 2)

        ms = assertMultistatusResponse(
            self.http.httpXmlRequest('PROPPATCH', '/webdavtests/proppatch_rm_unknown/res0', proppatch5_rm_unknown),
            numResponses=1)
        response = ms.get_first_response()
        unknown = response.get_property(ns, 'unknown_prop')
        if unknown is None:
            raise Exception('missing property in response')

        ms = assertMultistatusResponse(
            self.http.httpXmlRequest('PROPPATCH', '/webdavtests/proppatch_rm_unknown/res1', proppatch5_rm_unknown_set),
            numResponses=1)
        response = next(iter(ms.response.values()))
        unknown = response.get_property(ns, 'unknown_prop')
        myprop = response.get_property(ns, 'myprop')
        if unknown is None or myprop is None:
            raise Exception('missing property in response')

        if unknown.status != 200 or myprop.status != 200:
            raise Exception('wrong property status code')

