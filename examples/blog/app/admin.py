from src.hotpot.app import Hotpot
from src.hotpot.wrappers import Request, JSONResponse
from src.hotpot.utils import login_required, redirect, login, logout

app = Hotpot(main_app=False, name="admin", base_rule="/admin")


@app.route("/")
def admin_home(_app: Hotpot, request: Request):
    @login_required(security_key=_app.security_key, fail_redirect=redirect("/"))  # redirect to "/" other than "/admin/"
    def wrap(_app, request):
        return {"Admin home": "This is the admin home (need login)"}

    return wrap(_app, request)


@app.route("/user_info")
def admin_user(_app: Hotpot, request: Request):
    @login_required(security_key=_app.security_key, fail_redirect=redirect("/"))
    def wrap(_app: Hotpot, request):
        return _app.app_global.db['user']

    return wrap(_app, request)


@app.route("/login")
def admin_login(_app: Hotpot, request: Request):
    if request.method == "POST":
        user = _app.app_global.db['user']
        form_name = request.form['name']
        form_pwd = request.form['pwd']
        if user['name'] == form_name and user['pwd'] == form_pwd:
            response = JSONResponse({"Msg": "Successfully Log In!"})
            login(user['uid'], response, _app.security_key)
            return response
        else:
            response = JSONResponse({"Msg": "Failed Log In!"})
            return response
    else:
        return {
            "Msg": "Please log in with POST Method"
        }


@app.route("/logout")
def admin_logout(_app: Hotpot, request: Request):
    response = JSONResponse({"Msg": "Successfully Log Out!"})
    logout(response)
    return response
