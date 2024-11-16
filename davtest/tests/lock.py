import davtest.test
import davtest.webdav

from davtest.webdav import assertMultistatusResponse
from davtest.webdav import assertProperty

lock_request1 = """<?xml version="1.0" encoding="utf-8" ?>
<D:lockinfo xmlns:D='DAV:'>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockinfo>
"""


class TestLock(davtest.test.WebdavTest):
    def test_lock(self):
        self.create_testdata('lock1', 1)

        res = self.http.httpXmlRequest('LOCK', '/webdavtests/lock1/res0', lock_request1, hdrs={'Timeout': 'Second-10'})

        if res.status != 200:
            raise Exception(f'LOCK failed: {res.status}')

        lockdiscovery = davtest.webdav.LockDiscovery(res.body)
        locktoken = lockdiscovery.locks[0].locktoken

        res = self.http.doRequest('UNLOCK', '/webdavtests/lock1/res0', hdrs={'Lock-Token': f'<{locktoken}>'})

        # usually UNLOCK should respond with 204, however the spec doesn't
        # say that 200 (with response body) is forbidden
        if res.status != 204 and res.status != 200:
            raise Exception(f'UNLCOK: unexpected status code: {res.status}')

    def test_lock_put(self):
        self.create_testdata('lock2', 1)

        res = self.http.httpXmlRequest('LOCK', '/webdavtests/lock2/res0', lock_request1, hdrs={'Timeout': 'Second-10'})

        if res.status != 200:
            raise Exception(f'LOCK failed: {res.status}')

        with davtest.webdav.Lock(self.http, '/webdavtests/lock2/res0', res.body) as lock:
            res = self.http.doRequest('PUT', '/webdavtests/lock2/res0', 'new content', hdrs={'If': f'(<{lock.locktoken}>)'})
            if res.status > 299:
                raise Exception(f'PUT failed: {res.status}')


    def test_lock_put_without_token(self):
        self.create_testdata('lock3', 1)

        res = self.http.httpXmlRequest('LOCK', '/webdavtests/lock3/res0', lock_request1, hdrs={'Timeout': 'Second-10'})
        if res.status != 200:
            raise Exception(f'LOCK failed: {res.status}')

        with davtest.webdav.Lock(self.http, '/webdavtests/lock3/res0', res.body) as lock:
            res = self.http.doRequest('PUT', '/webdavtests/lock3/res0', 'new content')
            if res.status < 400:
                raise Exception(f'expected PUT to fail: {res.status}')

    def test_lock_create_res(self):
        self.create_testdata('lock4', 1)

        res = self.http.httpXmlRequest('LOCK', '/webdavtests/lock4/res_new', lock_request1, hdrs={'Timeout': 'Second-20'})
        lock_status = res.status
        # check lock_status later

        lockdiscovery = davtest.webdav.LockDiscovery(res.body)
        locktoken = lockdiscovery.locks[0].locktoken

        if not davtest.webdav.resource_exists(self.http, '/webdavtests/lock4/res_new'):
            raise Exception('resource does not exist')

        res = self.http.doRequest('UNLOCK', '/webdavtests/lock4/res_new', hdrs={'Lock-Token': f'<{locktoken}>'})
        if res.status >= 299:
            raise Exception(f'UNLCOK failed: {res.status}')

        if not davtest.webdav.resource_exists(self.http, '/webdavtests/lock4/res_new'):
            raise Exception('resource does not exist after UNLOCK')

        if lock_status != 201:
            raise Exception(f'wrong LOCK status code: {lock_status}')

    def test_lock_refresh(self):
        self.create_testdata('lock5', 1)

        res = self.http.httpXmlRequest('LOCK', '/webdavtests/lock5/res0', lock_request1, hdrs={'Timeout': 'Second-10'})
        if res.status != 200:
            raise Exception(f'LOCK failed: {res.status}')

        lockdiscovery = davtest.webdav.LockDiscovery(res.body)
        locktoken = lockdiscovery.locks[0].locktoken

        res = self.http.doRequest('LOCK', '/webdavtests/lock5/res0', hdrs={'Lock-Token': f'<{locktoken}>'})
        if res.status != 200:
            self.http.doRequest('UNLOCK', '/webdavtests/lock5/res0', hdrs={'Lock-Token': f'<{locktoken}>'})
            raise Exception(f'refresh LOCK failed: {res.status}')

        newlockdiscovery = davtest.webdav.LockDiscovery(res.body)
        newlocktoken = lockdiscovery.locks[0].locktoken

        res = self.http.doRequest('UNLOCK', '/webdavtests/lock5/res0', hdrs={'Lock-Token': f'<{newlocktoken}>'})
        if res.status >= 299:
            raise Exception(f'UNLCOK failed: {res.status}')

    def test_lock_indirect(self):
        self.create_testdata('lock6', 2)

        res = self.http.httpXmlRequest('LOCK', '/webdavtests/lock6/', lock_request1, hdrs={'Timeout': 'Second-30'})
        if res.status != 200:
            raise Exception(f'LOCK failed: {res.status}')

        # child resources should be locked, test put without locktoken
        with davtest.webdav.Lock(self.http, '/webdavtests/lock6/', res.body) as lock:
            res = self.http.doRequest('PUT', '/webdavtests/lock6/res0', 'new content')
            if res.status < 400:
                raise Exception(f'expected PUT to fail: {res.status}')
