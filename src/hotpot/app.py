from typing import Callable, Union
import configparser
import base64

from werkzeug.serving import run_simple
from werkzeug.wrappers import Response as ResponseBase, Request as RequestBase
from werkzeug.routing import Map, Rule, MapAdapter
from werkzeug.exceptions import *
from cryptography.fernet import Fernet

from .globals import AppGlobal
from .wrappers import Request, JSONResponse
from .utils import join_rules, StyledJSON


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

    def __init__(self, main_app=True, name="", base_rule="/"):
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
        # main_app for checking whether the app is considered as main app or combined to the main app
        self.main_app = main_app
        # name for namespace
        self.name = name
        # base_rule
        self.base_rule = base_rule
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
        self.exception_400 = lambda _app, e: JSONResponse(StyledJSON(code=400, messaga="Invalid Request"))
        self.exception_401 = lambda _app, e: JSONResponse(StyledJSON(code=401, messaga="Unauthorized"))
        self.exception_403 = lambda _app, e: JSONResponse(StyledJSON(code=403, messaga="Forbidden"))
        self.exception_404 = lambda _app, e: JSONResponse(StyledJSON(code=404, messaga="Not Found"))
        self.exception_406 = lambda _app, e: JSONResponse(StyledJSON(code=406, messaga="Not Acceptable"))
        self.exception_410 = lambda _app, e: JSONResponse(StyledJSON(code=410, messaga="Gone"))
        self.exception_422 = lambda _app, e: JSONResponse(StyledJSON(code=422, messaga="Unprocessable Entity"))
        self.exception_500 = lambda _app, e: JSONResponse(StyledJSON(code=500, messaga="Internal Server Error"))
        # api help doc
        self._api_help_doc = {}

    def __del__(self):
        # run all methods which after app end
        if self.main_app:
            for f in self._after_app:
                f(self)

    def __call__(self, environ, start_response):
        wsgi_app_response = self.wsgi_app(environ=environ, start_response=start_response)
        return wsgi_app_response

    # -------------Decorator Begin-------------
    def api_help_doc(self):
        return self._api_help_doc

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
    def combine_app(self, other_app: 'Hotpot'):

        # combine self and other app url_map together
        for _, rule_list in other_app.url_map._rules_by_endpoint.items():
            rule = rule_list[0]  # type:Rule
            self.url_map.add(rule.empty())

        # combine self and other app view_functions together
        for function_name, view_function in other_app.view_functions.items():
            self.view_functions[function_name] = view_function

        # Note: Config will not be influenced or changed by combing other app
        # Same as: security_key,app_global,exception_all,exception_404

        # combine self and other before_app function together
        for f in other_app._after_app:
            self._after_app.append(f)

        # combine self and other before_request function together
        for f in other_app._before_request:
            self._before_request.append(f)

        # combine self and other after_request function together
        for f in other_app._after_request:
            self._after_request.append(f)

        # combine self and other before_response function together
        for f in other_app._before_response:
            self._before_response.append(f)

        # combine self and other before_response function together
        for f in other_app._after_response:
            self._after_response.append(f)

        # Finally Del the other app
        del other_app

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
        # reload config
        self.security_key = self.config.get("security_key", b'YgHfXTZRK1t_tTGOh139WEpEii5gkqobuD89U7er1Ls=')

    def run(self):
        """
        Simple WSGI Server for development other than production
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
            response_or_dict = self.view_functions[endpoint](self, request, **values)
            if isinstance(response_or_dict, dict):
                return JSONResponse(response_or_dict)
            elif isinstance(response_or_dict, ResponseBase):
                return response_or_dict
            else:
                raise HTTPException("Service Error: Unsupported Response")
        except HTTPException as e:
            if self.exception_all is not None:
                return self.exception_all(self, e)
            if isinstance(e, NotFound):
                return self.exception_404(self, e)
            if isinstance(e, BadRequest):
                return self.exception_400(self, e)
            if isinstance(e, Unauthorized):
                return self.exception_401(self, e)
            if isinstance(e, Forbidden):
                return self.exception_403(self, e)
            if isinstance(e, NotAcceptable):
                return self.exception_406(self, e)
            if isinstance(e, Gone):
                return self.exception_410(self, e)
            if isinstance(e, UnprocessableEntity):
                return self.exception_422(self, e)
            if isinstance(e, InternalServerError):
                return self.exception_500(self, e)
            return e

    def wsgi_app(self, environ, start_response):
        # Request Start, call all methods in _before_request
        for f in self._before_request:
            f(self)
        request = Request(environ)
        # Request End, call all methods in _after_request
        for f in self._after_request:
            request = f(self, request)

        # Response Star, call all methods in _before_response
        for f in self._before_response:
            f(self)
        response = self.dispatch_request(request=request)
        # Response End, call all methods in _after_response
        for f in self._after_response:
            response = f(self, response)

        return response(environ, start_response)

    def route(self, rule, endpoint: str = None, **options):
        """
        Map url path to view functions (or say endpoints)
        Ex.
        @route("/")
        def index(_app,request):
            return {}

        !!!Important Note:
        (1) if two or more routes have same rule, say "/", but different endpoint name, the first defined Rule will be called
        (2) if two or more routes have same rule and same endpoint name, the last defined Rule will be called
        :param rule: url path, like "/"
        :param endpoint: explicitly set endpoint, or it will be function name
        :param options:
        :return:
        """

        def decorator(f: Callable):
            _endpoint = endpoint
            _rule = join_rules(self.base_rule, rule)
            if _endpoint is None:
                _endpoint = f.__name__
            _endpoint = self.name + "." + _endpoint
            self.view_functions[_endpoint] = f
            self.url_map.add(Rule(_rule, endpoint=_endpoint))

            # add to api help doc
            rule_description = f.__doc__
            if rule_description is None:
                rule_description = ""
            self._api_help_doc[rule] = rule_description.strip()

        return decorator

    # -----------handle http exception Start-----------
    def view_exception_all(self):
        """
       set custom views for all http exceptions
       Ex.
       @app.view_exception_all()
       def view_exception_all(_app,error):
           if isinstance(error,NOT_FOUND):
                return JSONResponse({"Not_Found": 404})
           return JSONResponse({"": 000})
       :return:

       Note: if use this function, all other view exception will not work.
        """

        def decorator(f: Callable[['Hotpot', HTTPException], ResponseBase]):
            self.exception_all = f

        return decorator

    def view_exception(self, code):
        """
        set view for http 404
        Ex.
        @app.view_exception_404()
        def view_exception_404(_app,error):
            print(error)
            return JSONResponse({"HttpException": 404})
        :return:
        """

        def decorator(f: Callable[['Hotpot', HTTPException], ResponseBase]):
            if code not in (400, 401, 403, 404, 406, 410, 422, 500):
                raise ValueError(
                    f"http code {code} is not supported, please use view_exception_all to customize your view function for your http exceptions")
            self.exception_404 = f
            setattr(self, f"exception_{code}", f)

        return decorator

    # -----------handle http exception End-----------
