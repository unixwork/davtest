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

import inspect
import sys
import http.client
import logging
import html

from davtest.connection import Http
import davtest.logging

from davtest.webdav import assertMultistatusResponse
from davtest.webdav import assertProperty

import davtest.basictests

test_classes = []


def dav_testsuite_run(config):
    davtest.logging.setup_logging()

    # create Http object for connection config
    http = Http(config)

    # run basic tests to make sure, the url is webdav-enabled
    # these tests must be completed
    print("run basic tests", file=sys.stderr)
    if not davtest.basictests.basic_tests(http):
        print("abort", file=sys.stderr)
        return False

    print("run test suite", file=sys.stderr)

    testresults = []

    for test_cls in test_classes:
        test = test_cls()
        test.http = http
        test.id = "x"


        for name, method in inspect.getmembers(test_cls, inspect.isfunction):
            if(name.startswith("test")):
                print(name + " ... ", end="", file=sys.stderr)
                test.http.requests.clear()
                error = True
                errorstr = ""
                try:
                    test.error = None
                    test_method = getattr(test, name)
                    test_method()
                    print("ok", file=sys.stderr)
                except Exception as err:
                    print(err, file=sys.stderr)
                    errorstr = err
                    error = False

                result = TestResult(error, test.http.requests.copy())
                result.name = name
                result.error = errorstr
                testresults.append(result)

    output_file = "testresults.html"
    if 'output' in config:
        output_file = config['output']

    with OutputWriter(output_file) as output:
        for result in testresults:
            output.add_result(result)

    return True

class OutputWriter:
    def __init__(self, path):
        self.file = open(path, "w")

    def __enter__(self):
        self.file.write("<html>\n")
        self.file.write("<head>\n")
        self.file.write("<title>davtest result</title>\n")
        self.file.write("</head>\n")
        self.file.write("<body>\n")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        #self.file.write("</body>\n")
        try:
            self.file.write("</body>\n")
        except Exception as err:
            pass
        self.file.close()

    def add_result(self, result):
        self.file.write("<div>\n")
        status = "ok" if result.result else result.error
        self.file.write(f"<h3>{result.name}: {status}</h3>\n")
        for req in result.requests:
            self.file.write("<div class='result_request'>\n")
            self.file.write("<pre>\n")
            self.file.write(html.escape(req[0]))
            self.file.write("</pre>\n")
            self.file.write("<pre>\n")
            self.file.write(html.escape(req[1]))
            self.file.write("</pre><hr/>\n")
            self.file.write("</div>\n")
        self.file.write("</div>\n")


class TestResult:
    def __init__(self, result, requests):
        self.result = result
        self.requests = requests

class WebdavTest:
    def __init_subclass__(cls, *args, **kwargs):
        test_classes.append(cls)

    # Tests if the status code is the expected value
    # If it is not the expected value, but in the nonerror range between
    # nonerror_from and nonerror_to, no exception is thrown
    def assert_statuscode(self, code, expected, nonerror_from=None, nonerror_to=None):
        if code == expected:
            return

        if nonerror_from is not None and nonerror_to is not None:
            if code >= nonerror_from and code <= nonerror_to:
                # add status code warning
                return

        raise Exception(f'expected status code: {expected}')

    def assert_resource_exists(self, path):
        if not davtest.webdav.resource_exists(self.http, path):
            raise Exception(f'expected resource does not exist: {path}')

    def assert_property(response, ns, propname, content=None, status=None):
        assertProperty(response, ns, propname, content, status)

    def create_testdata(self, colname, num_res):
        path = f'/webdavtests/{colname}/'
        res = self.http.doRequest('MKCOL', path)
        if res.status != 201:
            raise Exception(f'cannot create test collection: {res.status}')

        for i in range(num_res):
            res_path = f'{path}res{i}'
            res = self.http.doRequest('PUT', res_path, f'testcontent {i}')
            if res.status > 299:
                raise Exception(f'cannot create test resource {1}: {res.status}')

