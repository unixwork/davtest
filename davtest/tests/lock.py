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

        res = self.http.httpXmlRequest('UNLOCK', '/webdavtests/lock1/res0', lock_request1, hdrs={'Lock-Token': f'<{locktoken}>'})

        if res.status > 299:
            raise Exception(f'UNLCOK failed: {res.status}')





