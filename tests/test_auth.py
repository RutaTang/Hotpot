from unittest import TestCase
from src.hotpot.auth import Token, SECURITY_KEY


class TestAuth(TestCase):
    def test_token(self):
        # test get_token,get_data
        token = Token(SECURITY_KEY)
        token_str = token.get_token({"name": "hotpot"})
        data = token.get_data(token_str)
        self.assertEqual('hotpot',data["name"])

        # test __call__
        token = Token(SECURITY_KEY)
        token_str = token({"name": "hotpot"})
        data = token(token_str)
        self.assertEqual('hotpot',data["name"])