from unittest import TestCase

from werkzeug.wrappers import Response as ResponseBase, Request as RequestBase
from werkzeug.test import Client, EnvironBuilder
from werkzeug.datastructures import Headers
from cryptography.fernet import Fernet

from src.hotpot.app import Hotpot
from src.hotpot.sessions import get_session, set_session, clear_session
from src.hotpot.utils import redirect


class TestSessions(TestCase):
    def setUp(self) -> None:
        self.app = Hotpot()

    def test_set_sessions(self):
        response = ResponseBase("index")
        set_session({"uid": "1"}, response, self.app.security_key)
        cookie = response.headers.get("Set-Cookie", None)
        self.assertIsNotNone(cookie)

    def test_get_sessions(self):
        f = Fernet(self.app.security_key)
        cookie = f.encrypt(bytes('uid=1;', "utf-8"))
        headers = Headers()
        headers.add("Cookie", f"hotpot={str(cookie, 'utf-8')}")
        environ = EnvironBuilder("/", headers=headers)

        request = RequestBase(environ.get_environ())

        self.assertEqual({'uid': '1'}, get_session(request, self.app.security_key))

    def test_clear_sessions(self):
        response = ResponseBase("index")
        clear_session(response)
        cookie = response.headers.get("Set-Cookie")
        self.assertIsNotNone(cookie)