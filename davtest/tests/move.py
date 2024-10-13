import davtest.test
import davtest.webdav

from davtest.webdav import assertMultistatusResponse
from davtest.webdav import assertProperty

ns = "https://unixwork.de/davtest/"

proppatch_z_myprop = """<?xml version="1.0" encoding="utf-8" ?>
<D:propertyupdate xmlns:D="DAV:">
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

class TestMove(davtest.test.WebdavTest):
    def test_move_resource(self):
        self.create_testdata('move1', 1)

        destination = self.http.get_uri('/webdavtests/move1/res0_new')
        res = self.http.doRequest('MOVE', '/webdavtests/move1/res0', hdrs={'Destination': destination})

        if res.status > 299:
            raise Exception(f'MOVE status code: {res.status}')

        if not davtest.webdav.resource_exists(self.http, '/webdavtests/move1/res0_new'):
            raise Exception('resource does not exist')

        if davtest.webdav.resource_exists(self.http, '/webdavtests/move1/res0'):
            raise Exception('target resource still exists after MOVE')

    def test_move_collection(self):
        self.create_testdata('move2', 1)

        destination = self.http.get_uri('/webdavtests/move2_new/')
        res = self.http.doRequest('MOVE', '/webdavtests/move2/', hdrs={'Destination': destination})

        if res.status > 299:
            raise Exception(f'MOVE status code: {res.status}')

        if not davtest.webdav.resource_exists(self.http, '/webdavtests/move2_new/res0'):
            raise Exception('resource does not exist')

        if davtest.webdav.resource_exists(self.http, '/webdavtests/move2/'):
            raise Exception('target collection still exists after MOVE')


