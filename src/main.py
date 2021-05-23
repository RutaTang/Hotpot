import json

from hotpot.app import Hotpot
from hotpot.wrappers import JSONResponse
from hotpot.utils import redirect, login_required, login as login_, logout as logout_
from hotpot.sessions import set_session, get_session, clear_session

from tinydb import TinyDB
from werkzeug.serving import run_simple

app = Hotpot()




@app.after_app()
def del_db():
    print("del")


@app.route("/")
def index(request):
    json_object = {
        "Index": True,
    }
    return json_object


@app.route("/user_info")
@login_required(security_key=app.security_key, fail_redirect=redirect("/"))
def user_info(request):
    json_object = {
        "Name": "Ruta",
        "Age": 18,
    }
    return json_object


@app.route("/login")
def login(request):
    response = JSONResponse(json_object={})
    login_("1", response, security_key=app.security_key)
    return response


@app.route("/logout")
def logout(request):
    response = JSONResponse(json_object={})
    logout_(response)
    return response


@app.view_exception_404()
def view_exception_404(error):
    print(error)
    return JSONResponse({"HttpException": 404})


@app.view_exception_all()
def view_exception_all(error):
    print(error)
    return JSONResponse({"CustomException": 000})


@app.after_request()
def x_test(request):
    print(request.path)


app.run()
