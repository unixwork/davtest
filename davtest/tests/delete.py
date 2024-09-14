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
    def test_delete_res(self):
        res = self.http.doRequest('PUT', '/webdavtests/res_delete1', 'testcontent')
        if res.status > 299:
            raise Exception(f'cannot create test resource: {res.status}')

        res = self.http.doRequest('DELETE', '/webdavtests/res_delete1')
        if res.status < 200 or res.status > 299:
            raise Exception(f'DELETE failed: {res.status}')

        res = self.http.doRequest('GET', '/webdavtests/res_delete1')
        if res.status != 404:
            raise Exception(f'resource still exists after DELETE, status: {res.status}')

        exists = davtest.webdav.resource_exists(self.http, '/webdavtests/res_delete1')
        if exists:
            raise Exception('resource still exists after DELETE')

    def test_delete_col(self):
        # create test collections and resources_
        #
        # /col_delete2/
        # /col_delete2/res1
        # /col_delete2/sub_col/
        # /col_delete2/sub_col/res2

        res = self.http.doRequest('MKCOL', '/webdavtests/col_delete2/')
        if res.status > 299:
            raise Exception(f'cannot create test collection 1: {res.status}')

        res = self.http.doRequest('MKCOL', '/webdavtests/col_delete2/sub_col/')
        if res.status > 299:
            raise Exception(f'cannot create test collection 2: {res.status}')

        res = self.http.doRequest('PUT', '/webdavtests/col_delete2/res1', 'testcontent 1')
        if res.status > 299:
            raise Exception(f'cannot create test resource 1: {res.status}')

        res = self.http.doRequest('PUT', '/webdavtests/col_delete2/sub_col/res2', 'testcontent 2')
        if res.status > 299:
            raise Exception(f'cannot create test resource 2: {res.status}')

        # delete collection
        res = self.http.doRequest('DELETE', '/webdavtests/col_delete2/')
        if res.status < 200 or res.status > 299:
            raise Exception(f'DELETE failed: ' + str(res.status))

        # check if all collections and resources are deleted
        exists = davtest.webdav.resource_exists(self.http, '/webdavtests/col_delete2/')
        if exists:
            raise Exception('collection 1 still exists after DELETE')

        exists = davtest.webdav.resource_exists(self.http, '/webdavtests/col_delete2/sub_col/')
        if exists:
            raise Exception('collection 2 still exists after DELETE')

        res = self.http.doRequest('GET', '/webdavtests/col_delete2/res1')
        if res.status != 404:
            raise Exception(f'resource 1 still exists after DELETE, status: {res.status}')

        res = self.http.doRequest('GET', '/webdavtests/col_delete2/sub_col/res2')
        if res.status != 404:
            raise Exception(f'resource 2 still exists after DELETE, status: {res.status}')

