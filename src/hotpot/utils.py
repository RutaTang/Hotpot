import functools
from typing import Callable

from werkzeug.utils import redirect as werkzeug_redirect
from werkzeug.wrappers import Request as RequestBase, Response as ResponseBase
from cryptography.fernet import Fernet


def generate_security_key():
    return Fernet.generate_key()


def join_rules(*rules):
    tmp_rule = ''.join([str(r) for r in rules])
    rule = ''
    meet_slash = False
    for i, c in enumerate(tmp_rule):
        if c == "/" and not meet_slash:
            rule = rule + c
            meet_slash = True
        if c == "/" and meet_slash:
            continue
        if c != "/":
            rule = rule + c
            meet_slash = False
    return rule


def redirect(location, code=302):
    """
    Redirect to location
    :param location: ex. "/"
    :param code: http status
    :return: response
    """
    return werkzeug_redirect(location=location, code=code)