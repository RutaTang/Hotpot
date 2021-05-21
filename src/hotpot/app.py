from typing import Callable, Union

from werkzeug.serving import run_simple
from werkzeug.wrappers import Response as ResponseBase
from werkzeug.routing import Map, Rule, MapAdapter
from werkzeug.exceptions import HTTPException

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

    def __init__(self, config: dict):
        self.url_map = Map([])
        self.view_functions = {}
        self.config = config
        # init AppGlobal
        self.app_global = AppGlobal()
        # Other methods need to run before app real end
        self._after_app_end = []
        # before_request
        self._before_request = []
        # after_request
        self._after_request = []

    def __del__(self):
        # run all methods which after app end
        for f in self._after_app_end:
            f()

    def __call__(self, environ, start_response):
        # Request Start, call all methods in _before_request
        for f in self._before_request:
            f()
        wsgi_app_response = self.wsgi_app(environ=environ, start_response=start_response)
        # Request End, call all methods in _after_request
        for f in self._after_request:
            f()
        return wsgi_app_response

    # -------------Decorator Begin-------------

    def before_app(self):
        """
        Run methods as app init
        Ex.
        @before_app()
        def init_db():
            print("init db")
        :return:
        """

        def decorator(f):
            f()
            return f

        return decorator

    def after_app(self):
        """
        Run methods as app del
        :return:
        """

        def decorator(f):
            self._after_app_end.append(f)
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
        :return:
        """

        def decorator(f):
            self._after_request.append(f)
            return f

        return decorator

    # -------------Decorator End -------------

    def run(self, hostname='localhost', port=8080, debug=True):
        """
        Simple WSGI Server for development other than production
        :param hostname:
        :param port:
        :param debug: if debug is True, automatically reload while file changes
        :return:
        """
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
            return e

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request=request)
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
