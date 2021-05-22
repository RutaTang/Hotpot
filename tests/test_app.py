from unittest import TestCase

from werkzeug.wrappers import Response as ResponseBase
from werkzeug.test import Client

from src.hotpot.app import Hotpot


class TestApp(TestCase):
    def setUp(self) -> None:
        self.app = Hotpot()
        self.client = Client(self.app)

    def test_no_route(self):
        response = self.client.get("/")
        self.assertEqual(str(list(response[0])[0],'utf-8'),"Not Found")

    #TODO: more app test