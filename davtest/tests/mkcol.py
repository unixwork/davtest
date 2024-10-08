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

class TestMkcol(davtest.test.WebdavTest):
    def test_mkcol(self):
        conn = self.http.simpleRequest('MKCOL', '/webdavtests/mkcol_test1/')
        res = conn.getresponse()
        if res.status != 201:
            raise Exception(f'wrong status code: {res.status}')

        exists = davtest.webdav.resource_exists(self.http, '/webdavtests/mkcol_test1/')
        if not exists:
            raise Exception('collection does not exist after mkcol')

    def test_mkcol_existing_col(self):
        # create /webdavtests/mkcol_test2 and
        # try to create it again and check if the status code is 405 (Method Not Allowed)
        res = self.http.doRequest('MKCOL', '/webdavtests/mkcol_test2')
        if res.status != 201:
            raise Exception(f'wrong status code: {res.status}')

        res = self.http.doRequest('MKCOL', '/webdavtests/mkcol_test2')
        if res.status != 405:
            raise Exception(f'status code 405 expected, status code: {res.status}')

    def test_mkcol_missing_parent(self):
        res = self.http.doRequest('MKCOL', '/webdavtests/missing_collection/newcol/')
        if res.status != 409:
            raise Exception(f'status code 409 expected, status code: {res.status}')