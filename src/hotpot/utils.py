from werkzeug.utils import redirect as werkzeug_redirect


def redirect(location, code=302):
    return werkzeug_redirect(location=location, code=code)
