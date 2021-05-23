from unittest import TestCase

from werkzeug.wrappers import Response as ResponseBase, Request as RequestBase
from werkzeug.test import Client
from tinydb import TinyDB

from src.hotpot.app import Hotpot
from src.hotpot.wrappers import Request, JSONResponse


class TestApp(TestCase):
    def get_response_body(self, location: str):
        response = self.client.get(f"{location}")
        return str(list(response[0])[0], 'utf-8')

    def setUp(self) -> None:
        self.app = Hotpot()
        self.client = Client(self.app)

    def test_no_route(self):
        response = self.client.get("/")
        self.assertEqual(str(list(response[0])[0], 'utf-8'), "Not Found")

    # TODO: more app test
    def test_no_parameter_route(self):
        @self.app.route("/index1")
        def index1(request: Request):
            return {"index": 1}

        @self.app.route("/index2")
        def index2(request: Request):
            response = JSONResponse({"index": 2})
            return response

        self.assertEqual(self.get_response_body("/index1"), r'{"index": 1}')
        self.assertEqual(self.get_response_body("/index2"), r'{"index": 2}')

    def test_parameter_route(self):
        @self.app.route("/year/<int:year>/")
        def view_year(request: Request, year: int):
            return {"year": year}

        @self.app.route("/name/<string:name>/")
        def view_name(request: Request, name: str):
            return {"name": name}

        self.assertEqual(self.get_response_body("/year/2021/"), r'{"year": 2021}')
        self.assertEqual(self.get_response_body("/name/hotpot/"), r'{"name": "hotpot"}')

    def test_decorator_after_app(self):
        app = Hotpot()

        db = dict()
        db['test'] = 0
        app.app_global.db = db

        @app.after_app()
        def close_db(my_app: Hotpot):
            my_app.app_global.db['test'] = 1

        del app

        self.assertEqual(db['test'], 1)

    def test_decorator_after_request(self):
        @self.app.route("/")
        def index(request):
            return {"index": True}

        @self.app.after_request()
        def after_request(request) -> RequestBase:
            environ = request.environ
            environ['PATH_INFO'] = "/"
            new_request = RequestBase(environ)
            return new_request

        self.assertEqual(r'{"index": true}', self.get_response_body("/random"))

    def test_decorator_after_response(self):
        @self.app.route("/")
        def index(request):
            return {"index": True}

        @self.app.after_response()
        def after_response(response: ResponseBase) -> ResponseBase:
            response = ResponseBase(response=r'{"test":true}')
            return response

        self.assertEqual(r'{"test":true}', self.get_response_body("/"))

    # TODO: test all decorator before_xxx

    # TODO: test http exception view

    def test_view_exception_all(self):
        @self.app.view_exception_all()
        def view_exception_all(error):
            return JSONResponse({"Custom HttpException": True})

        @self.app.view_exception_404()
        def view_exception_404(error):
            return JSONResponse({"Not Found": True})

        self.assertNotEqual(self.get_response_body("/"), r'{"Not Found": true}')
        self.assertEqual(self.get_response_body("/"), r'{"Custom HttpException": true}')

    def test_view_exception_404(self):
        @self.app.view_exception_404()
        def view_exception_404(error):
            return JSONResponse({"Not Found": True})

        self.assertEqual(self.get_response_body("/"), r'{"Not Found": true}')
