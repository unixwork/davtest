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

import sys
import getopt

import davtest.test
import davtest.tests

# config
#
# url          base url for tests
# user         http auth user
# password     http auth password
config = dict()

# print help text
def helptext():
    print("Usage: davtest [-h] [-u <user>] [-p <password>] [-c <configfile>] <url>")

def main():
    # load config parameters from a file
    def loadconfig(config, file):
        with open(file) as f:
            for line in f:
                line = line.strip()
                pos = line.find('=')
                if len(line) > 3 and pos != -1 and line[0] != '#':
                    key, value = line.partition('=')[::2]
                    config.update({key.strip(): value.strip()})

    optlist, args = getopt.getopt(sys.argv[1:], 'hc:u:p:')

    # parse command line arguments
    if len(args) >= 1:
        config.update(url=args[0])

    for o, v in optlist:
        if o == '-h':
            helptext()
            exit(1)
        elif o == '-u':
            config.update(user=v)
        elif o == '-p':
            config.update(password=v)
        elif o == '-c':
            loadconfig(config, v)

    # check config
    err = False
    if 'url' not in config:
        print("Error: no url specified")
        err = True

    if 'user' not in config:
        print("Error: no user specified")
        err = True
    if 'password' not in config:
        print("Error: no password specified")

    if err:
        print("Abort.")
        helptext()
        exit(-1)

    # run test suite
    davtest.test.dav_testsuite_run(config)



if __name__ == "__main__":
    main()