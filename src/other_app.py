from hotpot.app import Hotpot
from hotpot.utils import login_required, redirect

app = Hotpot(main_app=False)


@app.route("/from_other_app")
def index_from_other_app(_app: 'Hotpot', requst):
    return {"Index": "From Other App"}


@app.before_request()
def before_request(_app):
    print("before request from other app")


@app.after_request()
def after_request(_app, request):
    print("after request from other app")
    return request


@app.before_response()
def before_response(_app):
    print("before response from other app")


@app.after_response()
def after_response(_app, response):
    print("after response from other app")
    return response


@app.after_app()
def after_app(_app):
    print("Del2")
