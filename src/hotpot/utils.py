import functools
from typing import Callable

from werkzeug.utils import redirect as werkzeug_redirect
from werkzeug.wrappers import Request as RequestBase, Response as ResponseBase
from .sessions import get_session, set_session, clear_session

from .app import Hotpot


def redirect(location, code=302):
    """
    Redirect to location
    :param location: ex. "/"
    :param code: http status
    :return: response
    """
    return werkzeug_redirect(location=location, code=code)


def login(uid: str, response: ResponseBase, security_key: bytes):
    """
    Simply login by setting uid in session
    :param uid: user id
    :param response:
    :param security_key:
    :return:
    """
    set_session({'uid': str(uid)}, response, security_key)


def logout(response: ResponseBase):
    """
    Simply logout by clear cookie which Name is 'hotpot' or KEY_NAME in sessions.py
    :param response:
    :return:
    """
    clear_session(response)


# -------Decorator-----------

def login_required(security_key: bytes, fail_redirect: ResponseBase):
    """
    This is !!!Decorator

    Login required by checking whether 'uid' is in session
    if uid is not none and uid is not "": access successful
    if uid is none or uid is "": access failed and return fail_redirect

    Ex.
    @app.route("/user_info")
    @login_required(app.security_key,redirect("/"))
    def user_info(request):
        return {"Name":"Ruta"}

    :param security_key: app security key for decrypt session info
    :param fail_redirect: can be redirect("/")
    :return:
    """

    def wrapper(f):
        @functools.wraps(f)
        def decorator(app: 'Hotpot', request: RequestBase):
            session_info = get_session(request, security_key=security_key)
            uid = session_info.get('uid', None)
            if uid is None:
                return fail_redirect
            if len(str(uid)) == 0:
                return fail_redirect
            return f(app,request)

        return decorator

    return wrapper
