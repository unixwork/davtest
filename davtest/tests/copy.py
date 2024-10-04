import davtest.test
import davtest.webdav

from davtest.webdav import assertMultistatusResponse

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