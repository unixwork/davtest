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


class TestUnlock(davtest.test.WebdavTest):
    def test_unlock(self):
        self.create_testdata('unlock1', 2)

        res = self.http.httpXmlRequest('LOCK', '/webdavtests/unlock1/res0', lock_request1, hdrs={'Timeout': 'Second-10'})

        if res.status != 200:
            raise Exception(f'LOCK failed: {res.status}')

        lockdiscovery = davtest.webdav.LockDiscovery(res.body)
        locktoken = lockdiscovery.locks[0].locktoken

        # try to unlock the wrong resource (res0 is locked, res1 is not)
        res = self.http.doRequest('UNLOCK', '/webdavtests/unlock1/res1', hdrs={'Lock-Token': f'<{locktoken}>'})
        status_fail = res.status

        # unlock correct resource
        res = self.http.doRequest('UNLOCK', '/webdavtests/unlock1/res0', hdrs={'Lock-Token': f'<{locktoken}>'})
        if res.status != 204 and res.status != 200:
            raise Exception(f'UNLCOK: unexpected status code: {res.status}')

        if status_fail != 409:
            raise Exception(f'expected 409: {status_fail}')