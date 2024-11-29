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

ns = "https://unixwork.de/davtest/"

proppatch2 = """<?xml version="1.0" encoding="utf-8" ?>
<D:propertyupdate xmlns:D="DAV:">
    <D:set>
        <D:prop>
            <Z:myprop xmlns:Z="https://unixwork.de/davtest/">testvalue1</Z:myprop>
        </D:prop>
    </D:set>
</D:propertyupdate>
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

    def test_lock_indirect_fail(self):
        self.create_testdata('lock7', 2)

        res = self.http.httpXmlRequest('LOCK', '/webdavtests/lock7/res0', lock_request1, hdrs={'Timeout': 'Second-30'})
        if res.status != 200:
            raise Exception(f'LOCK failed: {res.status}')

        with davtest.webdav.Lock(self.http, '/webdavtests/lock7/res0', res.body) as lock:
            res = self.http.httpXmlRequest('LOCK', '/webdavtests/lock7/', lock_request1, hdrs={'Timeout': 'Second-30'})

            if res.status == 207:
                pass
            elif res.status < 400:
                raise Exception(f'expected LOCK to fail: {res.status}')

    def test_lock_proppatch_without_token(self):
        self.create_testdata('lock8', 1)

        res = self.http.httpXmlRequest('LOCK', '/webdavtests/lock8/res0', lock_request1, hdrs={'Timeout': 'Second-10'})
        if res.status != 200:
            raise Exception(f'LOCK failed: {res.status}')

        with davtest.webdav.Lock(self.http, '/webdavtests/lock8/res0', res.body) as lock:
            # expect this proppatch request to fail
            # either directly with an error status code or with an error status code
            # for the requested property
            response = self.http.httpXmlRequest('PROPPATCH', '/webdavtests/lock8/res0', proppatch2)
            if response.status == 423:
                pass
            elif response.status == 207:
                ms = assertMultistatusResponse(response, numResponses=1)
                assertProperty(ms.get_first_response(), 'ns', 'myprop', status=200)
            else:
                raise Exception(f'unexpected status code {response.status}')

    def test_lock_copy_is_unlocked(self):
        # copy a locked resource and check if the new copy is locked
        #
        # Section 7.6:
        # A COPY method invocation MUST NOT duplicate any write locks active on
        # the source
        self.create_testdata('lock9', 1)

        res = self.http.httpXmlRequest('LOCK', '/webdavtests/lock9/res0', lock_request1, hdrs={'Timeout': 'Second-10'})
        if res.status != 200:
            raise Exception(f'LOCK failed: {res.status}')

        with davtest.webdav.Lock(self.http, '/webdavtests/lock9/res0', res.body) as lock:
            destination = self.http.get_uri('/webdavtests/lock9/res0_copy')
            res = self.http.doRequest('COPY', '/webdavtests/lock9/res0', hdrs={'Destination': destination})

            if res.status > 299:
                raise Exception(f'COPY status code: {res.status}')

            # test if we can update the resource without locktoken
            res = self.http.doRequest('PUT', '/webdavtests/lock9/res0_copy', 'new file content')
            if res.status > 299:
                raise Exception('failed to modify resource')

    def test_lock_move(self):
        self.create_testdata('lock10', 1)

        res = self.http.httpXmlRequest('LOCK', '/webdavtests/lock10/res0', lock_request1, hdrs={'Timeout': 'Second-10'})
        if res.status != 200:
            raise Exception(f'LOCK failed: {res.status}')

        with davtest.webdav.Lock(self.http, '/webdavtests/lock10/res0', res.body) as lock:
            destination = self.http.get_uri('/webdavtests/lock10/res0_moved')
            res = self.http.doRequest('MOVE', '/webdavtests/lock10/res0', hdrs={'Destination': destination})

            if res.status > 299:
                raise Exception(f'MOVE status code: {res.status}')

            # test if we can update the resource without locktoken
            res = self.http.doRequest('PUT', '/webdavtests/lock10/res0_moved', 'new file content')
            if res.status > 299:
                raise Exception('failed to modify resource')

    def test_lock_move_to_locked(self):
        self.create_testdata('lock11', 1)
        self.create_testdata('lock11_locked', 1)

        res = self.http.httpXmlRequest('LOCK', '/webdavtests/lock11_locked/', lock_request1, hdrs={'Timeout': 'Second-10'})
        if res.status != 200:
            raise Exception(f'LOCK failed: {res.status}')

        with davtest.webdav.Lock(self.http, '/webdavtests/lock11_locked', res.body) as lock:
            destination = self.http.get_uri('/webdavtests/lock11_locked/res_new')
            locktoken_uri = self.http.get_uri('/webdavtests/lock11_locked/')
            res = self.http.doRequest('MOVE', '/webdavtests/lock11/res0', hdrs={'Destination': destination, 'If': f'<{locktoken_uri}> (<{lock.locktoken}>)'})

            if res.status > 299:
                raise Exception(f'MOVE status code: {res.status}')

            res = self.http.doRequest('PUT', '/webdavtests/lock11/res_new', 'new content')
            if res.status < 400:
                raise Exception(f'expected PUT to fail: {res.status}')
