import unittest

from pyramid import testing
from . import TestBase, FunctionalTestBase


class TestSite(TestBase):
    "Unit and Integration tests"

    def test_homepage(self):
        from ..controllers.controllers import homepage

        request = testing.DummyRequest()
        response = homepage(request)

        self.assertEqual(response['project'], 'quranref')


class TestSiteFunctional(FunctionalTestBase):
    "Functional tests for the project"

    def test_get_login(self):
        res = self.app.get('/')
        self.assertEqual(res.status_int, 200)

