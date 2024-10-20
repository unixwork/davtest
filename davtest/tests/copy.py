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

class TestCopy(davtest.test.WebdavTest):
    def test_copy_resource(self):
        self.create_testdata('copy1', 1)

        destination = self.http.get_uri('/webdavtests/copy1/res0_new')
        res = self.http.doRequest('COPY', '/webdavtests/copy1/res0', hdrs={'Destination': destination})

        if res.status > 299:
            raise Exception(f'COPY status code: {res.status}')

        if not davtest.webdav.resource_exists(self.http, '/webdavtests/copy1/res0_new'):
            raise Exception('resource does not exist')

    def test_copy_collection(self):
        self.create_testdata('copy2', 1)

        destination = self.http.get_uri('/webdavtests/copy2_new')
        res = self.http.doRequest('COPY', '/webdavtests/copy2/', hdrs={'Destination': destination})

        if res.status > 299:
            raise Exception(f'COPY status code: {res.status}')

        if not davtest.webdav.resource_exists(self.http, '/webdavtests/copy2_new/'):
            raise Exception('collection does not exist')

        if not davtest.webdav.resource_exists(self.http, '/webdavtests/copy2_new/res0'):
            raise Exception('resource does not exist')

    def test_copy_overwrite_noheader(self):
        self.create_testdata('copy3', 1)
        self.create_testdata('copy3_target', 1)

        res = self.http.doRequest('PUT', '/webdavtests/copy3/res0', 'copy testcontent 1')
        if res.status > 299:
            raise Exception('failed to write test data 1')

        res = self.http.doRequest('PUT', '/webdavtests/copy3_target/res0', 'target testcontent 1')
        if res.status > 299:
            raise Exception('failed to write test data 2')

        destination = self.http.get_uri('/webdavtests/copy3_target/')
        res = self.http.doRequest('COPY', '/webdavtests/copy3/', hdrs={'Destination': destination})

        if res.status > 299:
            raise Exception(f'COPY status code: {res.status}')

        res = self.http.doRequest('GET', '/webdavtests/copy3_target/res0')
        if res.status != 200:
            raise Exception(f'GET failed: {res.status}')

        if res.body != b'copy testcontent 1':
            raise Exception('wrong content')

    def test_copy_overwrite(self):
        self.create_testdata('copy4', 1)
        self.create_testdata('copy4_target', 1)

        res = self.http.doRequest('PUT', '/webdavtests/copy4/res0', 'copy testcontent 1')
        if res.status > 299:
            raise Exception('failed to write test data 1')

        res = self.http.doRequest('PUT', '/webdavtests/copy4_target/res0', 'target testcontent 1')
        if res.status > 299:
            raise Exception('failed to write test data 2')

        destination = self.http.get_uri('/webdavtests/copy4_target/')
        res = self.http.doRequest('COPY', '/webdavtests/copy4/', hdrs={'Destination': destination, 'Overwrite': 'T'})

        if res.status > 299:
            raise Exception(f'COPY status code: {res.status}')

        res = self.http.doRequest('GET', '/webdavtests/copy4_target/res0')
        if res.status != 200:
            raise Exception(f'GET failed: {res.status}')

        if res.body != b'copy testcontent 1':
            raise Exception('wrong content')

    def test_copy_no_overwrite(self):
        self.create_testdata('copy5', 1)
        self.create_testdata('copy5_target', 1)

        res = self.http.doRequest('PUT', '/webdavtests/copy5/res0', 'copy testcontent 1')
        if res.status > 299:
            raise Exception('failed to write test data 1')

        res = self.http.doRequest('PUT', '/webdavtests/copy5_target/res0', 'target testcontent 1')
        if res.status > 299:
            raise Exception('failed to write test data 2')

        destination = self.http.get_uri('/webdavtests/copy5_target/')
        res = self.http.doRequest('COPY', '/webdavtests/copy5/', hdrs={'Destination': destination, 'Overwrite': 'F'})

        if res.status != 412:
            raise Exception(f'wrong COPY status code: {res.status}')

        res = self.http.doRequest('GET', '/webdavtests/copy5_target/res0')
        if res.status != 200:
            raise Exception(f'GET failed: {res.status}')

        if res.body != b'target testcontent 1':
            raise Exception('wrong content')

    def test_copy_deadprop(self):
        self.create_testdata('copy6', 1)

        # add a dead property, that should be copied later
        ms = assertMultistatusResponse(
            self.http.httpXmlRequest('PROPPATCH', '/webdavtests/copy6/res0', proppatch_z_myprop), numResponses=1)
        assertProperty(ms.get_first_response(), ns, 'myprop', status=200)

        # do copy
        destination = self.http.get_uri('/webdavtests/copy6/res0_new')
        res = self.http.doRequest('COPY', '/webdavtests/copy6/res0', hdrs={'Destination': destination})
        if res.status > 299:
            raise Exception('copy failed')

        # check property
        ms = assertMultistatusResponse(
            self.http.httpXmlRequest('PROPFIND', '/webdavtests/copy6/res0_new', propfind_z_myprop, 0),
            numResponses=1)
        assertProperty(ms.get_first_response(), ns, 'myprop', content='testvalue1', status=200)

    def test_copy_depth0(self):
        self.create_testdata('copy7', 1)

        # add a dead property to the collection, that should be copied later
        ms = assertMultistatusResponse(
            self.http.httpXmlRequest('PROPPATCH', '/webdavtests/copy7/', proppatch_z_myprop), numResponses=1)
        assertProperty(ms.get_first_response(), ns, 'myprop', status=200)

        # do copy
        destination = self.http.get_uri('/webdavtests/copy7_new/')
        res = self.http.doRequest('COPY', '/webdavtests/copy7/', hdrs={'Destination': destination, 'Depth': '0'})
        if res.status > 299:
            raise Exception('copy failed')

        # check property
        ms = assertMultistatusResponse(
            self.http.httpXmlRequest('PROPFIND', '/webdavtests/copy7_new/', propfind_z_myprop, 0),
            numResponses=1)
        assertProperty(ms.get_first_response(), ns, 'myprop', content='testvalue1', status=200)

        # check if copy7/res0 was copied
        # it shouldn't exist, because of Depth: 0
        exists = davtest.webdav.resource_exists(self.http, '/webdavtests/copy7_new/res0')
        if exists:
            raise Exception('child resource should not be copied')

    def test_copy_status201(self):
        self.create_testdata('copy8', 1)

        destination = self.http.get_uri('/webdavtests/copy8/res0_new')
        res = self.http.doRequest('COPY', '/webdavtests/copy8/res0', hdrs={'Destination': destination})

        if res.status != 201:
            raise Exception(f'COPY status code: {res.status}')


    def test_copy_status204(self):
        self.create_testdata('copy9', 2)

        destination = self.http.get_uri('/webdavtests/copy9/res1')
        res = self.http.doRequest('COPY', '/webdavtests/copy9/res0', hdrs={'Destination': destination})

        if res.status != 204:
            raise Exception(f'COPY status code: {res.status}')

    def test_copy_status409(self):
        self.create_testdata('copy10', 1)

        destination = self.http.get_uri('/webdavtests/copy10/sub/res0')
        res = self.http.doRequest('MOVE', '/webdavtests/copy10/res0', hdrs={'Destination': destination})

        if res.status != 409:
            raise Exception(f'COPY status code: {res.status}')
