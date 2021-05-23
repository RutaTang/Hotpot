from typing import Callable, Union
import configparser
import base64

from werkzeug.serving import run_simple
from werkzeug.wrappers import Response as ResponseBase, Request as RequestBase
from werkzeug.routing import Map, Rule, MapAdapter
from werkzeug.exceptions import HTTPException, NotFound
from cryptography.fernet import Fernet

from .globals import AppGlobal
from .wrappers import Request, JSONResponse


class Hotpot(object):
    """
    This is the core part of the web framework.
    WSGI Server will call the instance of this Class to process request.

    Ex.
    app = Hotpot(config={})
    @app.route("/)
    def index(request,**values):
        return {"Example":True}
    """

    def __init__(self):
        self.url_map = Map([])
        self.view_functions = {}
        self.config = {
            # Default Config
            "hostname": 'localhost',
            "port": 8080,
            "debug": True,
            # security key for session
            "security_key": b'YgHfXTZRK1t_tTGOh139WEpEii5gkqobuD89U7er1Ls=',
        }
        # security key for session ref to config['security_key']
        self.security_key = self.config.get("security_key", b'YgHfXTZRK1t_tTGOh139WEpEii5gkqobuD89U7er1Ls=')
        # init AppGlobal
        self.app_global = AppGlobal()
        # after_app
        self._after_app = []
        # before_request
        self._before_request = []
        # after_request
        self._after_request = []
        # before_response
        self._before_response = []
        # after_response
        self._after_response = []
        # HttpExceptions view functions
        self.exception_all = None
        self.exception_404 = lambda e: ResponseBase("Not Found")

    def add_config(self, config: Union[dict, str]):
        """
        Add Config to self.config
        :param config: dict or str; if str, it should be a path.
        :return:
        """
        if isinstance(config, dict):
            self.config = config
        elif isinstance(config, str):
            config_parser = configparser.ConfigParser()
            config_parser.read(config)
            self.config = config_parser._sections
        else:
            raise TypeError("config should be dict or str (path)")

    def __del__(self):
        # run all methods which after app end
        for f in self._after_app:
            f(self)

    def __call__(self, environ, start_response):
        wsgi_app_response = self.wsgi_app(environ=environ, start_response=start_response)
        return wsgi_app_response

    # -------------Decorator Begin-------------

    def after_app(self):
        """
        Run methods as app del
        :return:
        """

        def decorator(f):
            self._after_app.append(f)
            return f

        return decorator

    def before_request(self):
        """
        Run methods before each request
        :return:
        """

        def decorator(f):
            self._before_request.append(f)
            return f

        return decorator

    def after_request(self):
        """
        Run methods after each request
        f must have a parameter position to get request and return a request: f(request)->RequestBase
        Ex.
        @after_request()
        def after_request(request) -> RequestBase:
            environ = request.environ
            return RequestBase(environ)
        :return:
        """

        def decorator(f: Callable[[RequestBase], RequestBase]):
            self._after_request.append(f)
            return f

        return decorator

    def before_response(self):
        """
        Run methods before each response
        :return:
        """

        def decorator(f):
            self._before_response.append(f)
            return f

        return decorator

    def after_response(self):
        """
        Run methods after each response
        f must have a parameter position to get response and return a response: f(response) -> ResponseBase
        Ex.
        @after_response()
        def after_response(response) -> ResponseBase:

        :return:
        """

        def decorator(f):
            self._after_response.append(f)
            return f

        return decorator

    # -------------Decorator End -------------

    def run(self):
        """
        Simple WSGI Server for development other than production
        :param hostname:
        :param port:
        :param debug: if debug is True, automatically reload while file changes
        :return:
        """
        hostname = self.config.get("hostname", "localhost")
        port = self.config.get("port", 8080)
        debug = self.config.get("debug", True)
        run_simple(hostname, port, self, use_reloader=debug, use_debugger=debug)

    def dispatch_request(self, request) -> Union[ResponseBase, HTTPException]:
        adapter = self.url_map.bind_to_environ(request.environ)  # type:MapAdapter
        try:
            endpoint, values = adapter.match()
            # route will return response or json dict
            # @app.route("/"
            # def index(request):
            #   return {"Name":""}
            #   #or
            #   return Response()
            response_or_dict = self.view_functions[endpoint](request, **values)
            if isinstance(response_or_dict, dict):
                return JSONResponse(response_or_dict)
            elif isinstance(response_or_dict, ResponseBase):
                return response_or_dict
            else:
                raise HTTPException("Service Error: Unsupported Response")
        except HTTPException as e:
            if self.exception_all is not None:
                return self.exception_all(e)
            if isinstance(e, NotFound):
                return self.exception_404(e)
            return e

    def wsgi_app(self, environ, start_response):
        # Request Start, call all methods in _before_request
        for f in self._before_request:
            f()
        request = Request(environ)
        # Request End, call all methods in _after_request
        for f in self._after_request:
            request = f(request)

        # Response Star, call all methods in _before_response
        for f in self._before_response:
            f()
        response = self.dispatch_request(request=request)
        # Response End, call all methods in _after_response
        for f in self._after_response:
            response = f(response)

        return response(environ, start_response)

    def route(self, rule, **options):
        """
        Map url path to view functions (or say endpoints)
        Ex.
        @route("/")
        def index(request):
            return {}
        :param rule: url path, like "/"
        :param options:
        :return:
        """

        def decorator(f: Callable):
            self.view_functions[f.__name__] = f
            self.url_map.add(Rule(rule, endpoint=f.__name__))

        return decorator

    # -----------handle http exception Start-----------
    def view_exception_all(self):
        """
       set custom views for all http exceptions
       Ex.
       @app.view_exception_all()
       def view_exception_all(error):
           if isinstance(error,NOT_FOUND):
                return JSONResponse({"Not_Found": 404})
           return JSONResponse({"": 000})
       :return:

       Note: if use this function, all other view exception will not work.
        """

        def decorator(f: Callable[[], ResponseBase]):
            self.exception_all = f

        return decorator

    def view_exception_404(self):
        """
        set view for http 404
        Ex.
        @app.view_exception_404()
        def view_exception_404(error):
            print(error)
            return JSONResponse({"HttpException": 404})
        :return:
        """

        def decorator(f: Callable[[], ResponseBase]):
            self.exception_404 = f

        return decorator

    # -----------handle http exception End-----------
