"""
Copyright 2011 Gregory Holt

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import unittest
from StringIO import StringIO
from uuid import uuid4

from swiftly.cli import CLI
from swiftly.test.functional import AUTH_URL, AUTH_USER, AUTH_KEY, \
    SWIFT_PROXY_STORAGE_PATH


class TestPost(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.start_args = ['-A', AUTH_URL, '-U', AUTH_USER, '-K', AUTH_KEY]

    def setUp(self):
        self.uuid = uuid4().hex
        self.container = 'swiftly_test_' + self.uuid
        self.obj = 'swiftly_test_' + self.uuid + '/test'

        stdout = StringIO()
        stderr = StringIO()
        args = list(self.start_args)
        args.extend(['put', self.container])
        cli = CLI(args=args, stdout=stdout, stderr=stderr)
        rv = cli.main()

        stdin = StringIO('testvalue')
        stdout = StringIO()
        stderr = StringIO()
        args = list(self.start_args)
        args.extend(['put', self.obj])
        cli = CLI(args=args, stdin=stdin, stdout=stdout, stderr=stderr)
        rv = cli.main()
        self.assertEquals(rv, 0)

    def tearDown(self):
        stdout = StringIO()
        stderr = StringIO()
        args = list(self.start_args)
        args.extend(['delete', self.container, '--recursive'])
        cli = CLI(args=args, stdout=stdout, stderr=stderr)
        cli.main()

    def test_post_obj(self):
        stdout = StringIO()
        stderr = StringIO()
        args = list(self.start_args)
        args.extend(['post', self.obj, '-h', 'x-object-meta-swiftly-test:one'])
        cli = CLI(args=args, stdout=stdout, stderr=stderr)
        rv = cli.main()
        self.assertEquals(rv, 0)
        self.assertEquals(stdout.getvalue(), '')
        self.assertEquals(stderr.getvalue(), '')

        stdout = StringIO()
        stderr = StringIO()
        args = list(self.start_args)
        args.extend(['head', self.obj])
        cli = CLI(args=args, stdout=stdout, stderr=stderr)
        rv = cli.main()
        self.assertEquals(rv, 0)
        stdout = \
            dict(x.split(':', 1) for x in stdout.getvalue().split('\n') if x)
        self.assertEquals(
            sorted(stdout.keys()),
            ['Content-Length', 'Content-Type', 'Etag', 'Last-Modified',
             'X-Object-Meta-Swiftly-Test', 'X-Timestamp'])
        self.assertEquals(stdout['Content-Length'].strip(), '9')
        self.assertEquals(stdout['Content-Type'].strip(),
                          'application/octet-stream')
        self.assertEquals(stdout['Etag'].strip(),
                          'e9de89b0a5e9ad6efd5e5ab543ec617c')
        self.assertEquals(stdout['X-Object-Meta-Swiftly-Test'].strip(),
                          'one')
        self.assertEquals(stderr.getvalue(), '')

    def test_post_container(self):
        stdout = StringIO()
        stderr = StringIO()
        args = list(self.start_args)
        args.extend(['post', self.container, '-h',
                     'x-container-meta-swiftly-test:one'])
        cli = CLI(args=args, stdout=stdout, stderr=stderr)
        rv = cli.main()
        self.assertEquals(rv, 0)
        self.assertEquals(stdout.getvalue(), '')
        self.assertEquals(stderr.getvalue(), '')

        stdout = StringIO()
        stderr = StringIO()
        args = list(self.start_args)
        args.extend(['head', self.container])
        cli = CLI(args=args, stdout=stdout, stderr=stderr)
        rv = cli.main()
        self.assertEquals(rv, 0)
        stdout = \
            dict(x.split(':', 1) for x in stdout.getvalue().split('\n') if x)
        self.assertEquals(
            sorted(stdout.keys()),
            ['X-Container-Bytes-Used', 'X-Container-Meta-Swiftly-Test',
             'X-Container-Object-Count', 'X-Timestamp'])
        self.assertEquals(stderr.getvalue(), '')

    def test_post_account(self):
        uuid = uuid4().hex
        stdout = StringIO()
        stderr = StringIO()
        args = list(self.start_args)
        args.extend(
            ['post', '-h', 'x-account-meta-swiftly-test-%s:one' % uuid])
        cli = CLI(args=args, stdout=stdout, stderr=stderr)
        rv = cli.main()
        self.assertEquals(rv, 0)
        self.assertEquals(stdout.getvalue(), '')
        self.assertEquals(stderr.getvalue(), '')

        stdout = StringIO()
        stderr = StringIO()
        args = list(self.start_args)
        args.extend(['head'])
        cli = CLI(args=args, stdout=stdout, stderr=stderr)
        rv = cli.main()
        self.assertEquals(rv, 0)
        stdout = \
            dict(x.split(':', 1) for x in stdout.getvalue().split('\n') if x)
        self.assertTrue('X-Account-Bytes-Used' in stdout)
        self.assertTrue('X-Account-Container-Count' in stdout)
        self.assertTrue('X-Account-Object-Count' in stdout)
        self.assertTrue(
            ('X-Account-Meta-Swiftly-Test-%s' % uuid).title() in stdout)
        self.assertEquals(stderr.getvalue(), '')

        stdout = StringIO()
        stderr = StringIO()
        args = list(self.start_args)
        args.extend(
            ['post', '-h', 'x-account-meta-swiftly-test-%s:' % uuid])
        cli = CLI(args=args, stdout=stdout, stderr=stderr)
        rv = cli.main()
        self.assertEquals(rv, 0)
        self.assertEquals(stdout.getvalue(), '')
        self.assertEquals(stderr.getvalue(), '')

        stdout = StringIO()
        stderr = StringIO()
        args = list(self.start_args)
        args.extend(['head'])
        cli = CLI(args=args, stdout=stdout, stderr=stderr)
        rv = cli.main()
        self.assertEquals(rv, 0)
        stdout = \
            dict(x.split(':', 1) for x in stdout.getvalue().split('\n') if x)
        self.assertTrue('X-Account-Bytes-Used' in stdout)
        self.assertTrue('X-Account-Container-Count' in stdout)
        self.assertTrue('X-Account-Object-Count' in stdout)
        self.assertTrue(
            ('X-Account-Meta-Swiftly-Test-%s' % uuid).title() not in stdout)
        self.assertEquals(stderr.getvalue(), '')


class TestDirectPost(TestPost):

    def __init__(self, *args, **kwargs):
        TestPost.__init__(self, *args, **kwargs)
        self.start_args = ['-D', SWIFT_PROXY_STORAGE_PATH]


if __name__ == '__main__':
    unittest.main()
