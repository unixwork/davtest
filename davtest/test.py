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

from davtest.connection import Http

import davtest.basictests

test_classes = []


def dav_testsuite_run(config):
    # create Http object for connection config
    http = Http(config)

    # run basic tests to make sure, the url is webdav-enabled
    # these tests must be completed
    print("run basic tests", file=sys.stderr)
    if not davtest.basictests.basic_tests(http):
        print("abort", file=sys.stderr)
        return False

    print("run test suite", file=sys.stderr)

    for test_cls in test_classes:
        test = test_cls()
        test.http = http
        test.id = "x"


        for name, method in inspect.getmembers(test_cls, inspect.isfunction):
            if(name.startswith("test")):
                print(name + " ... ", end="", file=sys.stderr)
                try:
                    test.error = None
                    test_method = getattr(test, name)
                    test_method()
                    print("ok", file=sys.stderr)
                except Exception as err:
                    print(err, file=sys.stderr)


    return True

class WebdavTest:
    def __init_subclass__(cls, *args, **kwargs):
        test_classes.append(cls)

