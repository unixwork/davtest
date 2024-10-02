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