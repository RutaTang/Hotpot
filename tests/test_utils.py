import os.path
from unittest import TestCase
from src.hotpot.utils import join_rules,redirect,generate_security_key


class TestUtils(TestCase):

    def test_join_rules(self):
        rules = ["/", "auth/"]
        self.assertEqual(join_rules(*rules), "/auth/")

        rules = ["", "auth/"]
        self.assertEqual(join_rules(*rules), "auth/")

        rules = ["/", "/auth/"]
        self.assertEqual(join_rules(*rules), "/auth/")

        rules = ["/", "/auth/", "/name/<string:name>"]
        self.assertEqual(join_rules(*rules), "/auth/name/<string:name>")

        rules = ["/", "/auth/uid<int:uid>", "/name/<string:name>"]
        self.assertEqual(join_rules(*rules), "/auth/uid<int:uid>/name/<string:name>")

    def test_redirect(self):
        redirect_path = "/"
        response = redirect(redirect_path)
        self.assertEqual(302,response.status_code)
        self.assertEqual(redirect_path, response.location)