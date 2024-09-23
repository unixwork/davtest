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

proppatch1 = """<?xml version="1.0" encoding="utf-8" ?>
<D:propertyupdate xmlns:D="DAV:">
    <D:set>
        <D:prop>
            <D:myprop>testvalue1</D:myprop>
        </D:prop>
    </D:set>
</D:propertyupdate>
"""

class TestProppatch(davtest.test.WebdavTest):
    def test_proppatch_set_response(self):
        self.create_testdata('proppatch_set1', 1)

        res = self.http.httpXmlRequest('PROPPATCH', '/webdavtests/proppatch_set1/res0', proppatch1)
        if res.status != 207:
            raise Exception(f'wrong status code: {res.status}')

        if len(res.body) == 0:
            raise Exception(f'no propfind response body')

        ms = davtest.webdav.Multistatus(res.body)
        if len(ms.response) != 1:
            raise Exception(f'wrong number of response elements')

        response = next(iter(ms.response.values()))
        prop = response.get_property('DAV:', 'myprop')
        errprop = response.get_property('DAV:', 'myprop')

        if prop is None and errprop is None:
            raise Exception('missing property in response')


