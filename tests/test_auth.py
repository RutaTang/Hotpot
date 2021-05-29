from unittest import TestCase
from src.hotpot.auth import Token, SECURITY_KEY


class TestAuth(TestCase):
    def test_token(self):
        token = Token(SECURITY_KEY)
        token_str = token.get_token({"name": "hotpot"})
        data = token.get_data(token_str)
        self.assertEqual('hotpot',data["name"])
