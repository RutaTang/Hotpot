import json

from hotpot.app import Hotpot
from hotpot.wrappers import JSONResponse
from hotpot.utils import redirect, login_required, login as login_, logout as logout_
from hotpot.sessions import set_session, get_session, clear_session
from src.other_app import app as other_app

from tinydb import TinyDB
from werkzeug.serving import run_simple

app = Hotpot()
app.app_global.db = {"uid": "1", "username": "hotpot", "pwd": "123"}
app.combine_app(other_app)



@app.after_app()
def del_db(current_app: Hotpot):
    current_app.app_global.db = dict()


@app.route("/")
def index(mapp, request):
    print(mapp)
    json_object = {
        "Index": True,
    }
    return json_object


@app.route("/user_info")
@login_required(security_key=app.security_key, fail_redirect=redirect("/"))
def user_info(mapp, request):
    return app.app_global.db


@app.route("/login")
def login(mapp, request):
    if request.method == "POST":
        username = request.form['username']
        pwd = request.form['pwd']
        if username == app.app_global.db['username'] and pwd == app.app_global.db['pwd']:
            response = JSONResponse(json_object={"Login Status": "Successful"})
            login_(app.app_global.db['uid'], response, security_key=app.security_key)
            return response
    else:
        return redirect("/")


@app.route("/logout")
def logout(mapp, request):
    response = JSONResponse(json_object={"Logout Status": "Successful"})
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


app.run()
