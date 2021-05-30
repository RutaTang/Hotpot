from unittest import TestCase

from werkzeug.wrappers import Response as ResponseBase, Request as RequestBase
from werkzeug.test import Client
from tinydb import TinyDB

from src.hotpot.app import Hotpot
from src.hotpot.wrappers import Request, JSONResponse


class TestApp(TestCase):

    def setUp(self) -> None:
        self.app = Hotpot()
        self.client = Client(self.app)

    def get_response_body(self, location: str, method="GET", client=None):
        if client is None:
            client = self.client
        if method == "GET":
            response = client.get(f"{location}")
        elif method == "POST":
            response = client.post(f"{location}")
        elif method == "PUT":
            response = client.put(f"{location}")
        elif method == "DELETE":
            response = client.delete(f"{location}")
        elif method == "PATCH":
            response = client.patch(f"{location}")
        else:
            raise RuntimeError("Not Supported HTTP Method")
        return str(list(response[0])[0], 'utf-8')

    def test_http_methods(self):
        @self.app.route("/")
        def index(_app: 'Hotpot', request: RequestBase):
            return ResponseBase(f"{request.method}")

        self.assertEqual("GET", self.get_response_body("/", method="GET"))
        self.assertEqual("POST", self.get_response_body("/", method="POST"))
        self.assertEqual("PUT", self.get_response_body("/", method="PUT"))
        self.assertEqual("DELETE", self.get_response_body("/", method="DELETE"))
        self.assertEqual("PATCH", self.get_response_body("/", method="PATCH"))

    def test_no_route(self):
        response = self.client.get("/")
        self.assertEqual(str(list(response[0])[0], 'utf-8'), "Not Found")

    def test_no_parameter_route(self):
        @self.app.route("/index1")
        def index1(_app, request: Request):
            return {"index": 1}

        @self.app.route("/index2")
        def index2(_app, request: Request):
            response = JSONResponse({"index": 2})
            return response

        self.assertEqual(self.get_response_body("/index1"), r'{"index": 1}')
        self.assertEqual(self.get_response_body("/index2"), r'{"index": 2}')

    def test_parameter_route(self):
        @self.app.route("/year/<int:year>/")
        def view_year(_app, request: Request, year: int):
            return {"year": year}

        @self.app.route("/name/<string:name>/")
        def view_name(_app, request: Request, name: str):
            return {"name": name}

        self.assertEqual(self.get_response_body("/year/2021/"), r'{"year": 2021}')
        self.assertEqual(self.get_response_body("/name/hotpot/"), r'{"name": "hotpot"}')

    def test_endpoint_same(self):
        @self.app.route("/explicit", endpoint="explicit")
        def explicit(_app, request):
            return ResponseBase("explicit")

        @self.app.route("/test1", endpoint="explicit")
        def explicit(_app, request):
            return ResponseBase("explicit_cover")

        @self.app.route("/implicit")
        def implicit(_app, request):
            return ResponseBase("implicit")

        @self.app.route("/implicit")
        def implicit(_app, request):
            return ResponseBase("implicit_cover")

        # last view function will cover previous one
        self.assertEqual("explicit_cover", self.get_response_body("/explicit"))
        self.assertEqual("implicit_cover", self.get_response_body("/implicit"))

    def test_endpoint_different(self):
        @self.app.route("/explicit", endpoint="explicit")
        def explicit(_app, request):
            return ResponseBase("explicit")

        @self.app.route("/explicit", endpoint="explicit2")
        def explicit2(_app, request):
            return ResponseBase("explicit2")

        @self.app.route("/implicit")
        def implicit(_app, request):
            return ResponseBase("implicit")

        @self.app.route("/implicit")
        def implicit2(_app, request):
            return ResponseBase("implicit2")

        # if same root, different endpoint name, the previous one will be used
        self.assertEqual("explicit", self.get_response_body("/explicit"))
        self.assertEqual("implicit", self.get_response_body("/implicit"))

    def test_different_root_same_endpoint(self):
        @self.app.route("/index", endpoint="index")
        def index(_app, request):
            return ResponseBase("index")

        @self.app.route("/index2", endpoint="index")
        def index(_app, request):
            return ResponseBase("index2")

        # if different root and same endpoint, last view function will be used for all routes that map to the function
        self.assertEqual("index2", self.get_response_body("/index"))
        self.assertEqual("index2", self.get_response_body("/index2"))

    def test_combine_app_common(self):
        app1 = Hotpot(main_app=True, name="app1")

        @app1.route("/app1/index")
        def index(_app, request):
            return ResponseBase("app1.index")

        app2 = Hotpot(main_app=False, name="app2")

        @app2.route("/app2/index")
        def index(_app, request):
            return ResponseBase("app2.index")

        app1.combine_app(app2)

        client = Client(app1)
        self.assertEqual("app1.index", self.get_response_body("/app1/index", client=client))
        self.assertEqual("app2.index", self.get_response_body("/app2/index", client=client))

    def test_combine_app_common_with_base_rule(self):
        app1 = Hotpot(main_app=True, name="app1", base_rule="/app1")

        @app1.route("/index")
        def index(_app, request):
            return ResponseBase("app1.index")

        app2 = Hotpot(main_app=False, name="app2", base_rule="/app2")

        @app2.route("/index")
        def index(_app, request):
            return ResponseBase("app2.index")

        app1.combine_app(app2)

        client = Client(app1)
        self.assertEqual("app1.index", self.get_response_body("/app1/index", client=client))
        self.assertEqual("app2.index", self.get_response_body("/app2/index", client=client))

    # ---------- test decorator about before(after)_request(response,app) ----------

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

    def test_decorator_before_request(self):
        @self.app.before_request()
        def before_request(_app: 'Hotpot'):
            _app.app_global.custom_variable = "hotpot"

        with self.assertRaises(KeyError):
            _ = self.app.app_global.custom_variable
        self.get_response_body("/")
        self.assertEqual("hotpot", self.app.app_global.custom_variable)

    def test_decorator_after_request(self):
        @self.app.route("/")
        def index(_app, request):
            return {"index": True}

        @self.app.after_request()
        def after_request(_app, request) -> RequestBase:
            environ = request.environ
            environ['PATH_INFO'] = "/"
            new_request = RequestBase(environ)
            return new_request

        self.assertEqual(r'{"index": true}', self.get_response_body("/random"))

    def test_decorator_before_response(self):
        @self.app.before_response()
        def before_response(_app: 'Hotpot'):
            _app.app_global.custom_variable = "hotpot"

        with self.assertRaises(KeyError):
            _ = self.app.app_global.custom_variable
        self.get_response_body("/")
        self.assertEqual("hotpot", self.app.app_global.custom_variable)

    def test_decorator_after_response(self):
        @self.app.route("/")
        def index(_app, request):
            return {"index": True}

        @self.app.after_response()
        def after_response(_app, response: ResponseBase) -> ResponseBase:
            response = ResponseBase(response=r'{"test":true}')
            return response

        self.assertEqual(r'{"test":true}', self.get_response_body("/"))

    # -------------test http exception view-------------

    def test_view_exception_all(self):
        @self.app.view_exception_all()
        def view_exception_all(_app, error):
            return JSONResponse({"Custom HttpException": True})

        @self.app.view_exception_404()
        def view_exception_404(_app, error):
            return JSONResponse({"Not Found": True})

        self.assertNotEqual(self.get_response_body("/"), r'{"Not Found": true}')
        self.assertEqual(self.get_response_body("/"), r'{"Custom HttpException": true}')

    def test_view_exception_404(self):
        @self.app.view_exception_404()
        def view_exception_404(_app, error):
            return JSONResponse({"Not Found": True})

        self.assertEqual(self.get_response_body("/"), r'{"Not Found": true}')
