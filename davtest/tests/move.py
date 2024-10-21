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

    def test_move_properties(self):
        self.create_testdata('move3', 1)

        # add a dead property, that should be copied later
        ms = assertMultistatusResponse(
            self.http.httpXmlRequest('PROPPATCH', '/webdavtests/move3/res0', proppatch_z_myprop), numResponses=1)
        assertProperty(ms.get_first_response(), ns, 'myprop', status=200)

        # do copy
        destination = self.http.get_uri('/webdavtests/move3/res0_new')
        res = self.http.doRequest('MOVE', '/webdavtests/move3/res0', hdrs={'Destination': destination})
        if res.status > 299:
            raise Exception('copy failed')

        # check property
        ms = assertMultistatusResponse(
            self.http.httpXmlRequest('PROPFIND', '/webdavtests/move3/res0_new', propfind_z_myprop, 0),
            numResponses=1)
        assertProperty(ms.get_first_response(), ns, 'myprop', content='testvalue1', status=200)

    def test_move_overwrite(self):
        self.create_testdata('move4', 1)
        self.create_testdata('move4_target', 2)

        res = self.http.doRequest('PUT', '/webdavtests/move4/res0', 'move4')
        if res.status > 299:
            raise Exception(f'cannot create test resource: {res.status}')

        res = self.http.doRequest('PUT', '/webdavtests/move4_target/res0', 'move4target')
        if res.status > 299:
            raise Exception(f'cannot create test resource: {res.status}')

        destination = self.http.get_uri('/webdavtests/move4_target/')
        res = self.http.doRequest('MOVE', '/webdavtests/move4/', hdrs={'Destination': destination, 'Overwrite': 'T'})

        if res.status > 299:
            raise Exception(f'MOVE status code: {res.status}')

        exists = davtest.webdav.resource_exists(self.http, '/webdavtests/move4_target/res1')
        if exists:
            raise Exception('res1 should not exist')

        res = self.http.doRequest('GET', '/webdavtests/move4_target/res0')
        if res.status != 200:
            raise Exception(f'GET failed: {res.status}')

        if res.body != b'move4':
            raise Exception('wrong content')

    def test_move_no_overwrite(self):
        self.create_testdata('move5', 1)
        self.create_testdata('move5_target', 2)

        destination = self.http.get_uri('/webdavtests/move5_target/')
        res = self.http.doRequest('MOVE', '/webdavtests/move5/', hdrs={'Destination': destination, 'Overwrite': 'F'})

        if res.status != 412:
            raise Exception(f'MOVE expected to fail, status code: {res.status}')

    def test_move_status201(self):
        self.create_testdata('move6', 1)

        destination = self.http.get_uri('/webdavtests/move6/res0_new')
        res = self.http.doRequest('MOVE', '/webdavtests/move6/res0', hdrs={'Destination': destination})

        if res.status != 201:
            raise Exception(f'MOVE status code: {res.status}')


    def test_move_status204(self):
        self.create_testdata('move7', 2)

        destination = self.http.get_uri('/webdavtests/move7/res1')
        res = self.http.doRequest('MOVE', '/webdavtests/move7/res0', hdrs={'Destination': destination})

        if res.status != 204:
            raise Exception(f'MOVE status code: {res.status}')

    def test_move_status409(self):
        self.create_testdata('move8', 1)

        destination = self.http.get_uri('/webdavtests/move8/sub/res0')
        res = self.http.doRequest('MOVE', '/webdavtests/move8/res0', hdrs={'Destination': destination})

        if res.status != 409:
            raise Exception(f'MOVE status code: {res.status}')

    def test_move_status412(self):
        self.create_testdata('move9', 2)

        destination = self.http.get_uri('/webdavtests/move9/res1')
        res = self.http.doRequest('MOVE', '/webdavtests/move9/res0', hdrs={'Destination': destination, 'Overwrite': 'F'})

        if res.status != 412:
            raise Exception(f'MOVE status code: {res.status}')