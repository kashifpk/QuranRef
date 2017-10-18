import unittest

import os.path

from pyramid import testing
from paste.deploy import appconfig
from webtest import TestApp

from .. import main

here = os.path.dirname(__file__)
if os.path.exists(os.path.join(here, '../../', 'test.ini')):
    settings = appconfig('config:' + os.path.join(here, '../../', 'test.ini'))


class TestBase(unittest.TestCase):
    "Base class for test cases (unit tests) tuned for pyck projects"

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        pass


class FunctionalTestBase(TestBase):

    @classmethod
    def setUpClass(cls):
        cls.app = main({}, **settings)
        super(FunctionalTestBase, cls).setUpClass()

    def setUp(self):
        self.app = TestApp(self.app)
        self.config = testing.setUp()
        super(FunctionalTestBase, self).setUp()
