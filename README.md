# Hotpot

**A tiny and easy python web framework just for your fun! :)**

<div style="text-align: center">
<img src="https://github.com/RutaTang/Hotpot/blob/master/artworks/hotpot.png?raw=true" style="width: 150px;height: 150px;">
</div>

Hotpot is designed **almost** just for JSON RESTful, but for sure, you can render template or transform data with xml as
you want.

*By the way, if you never know the hotpot, you may miss one of the most delicious,fragrant and tasty food in the world ~
\_~*

## Translation

[中文简体]()

## Installing

install and update hotpot using pip:

`pip install hotpot`

## A Simple App

```python
from hotpot.app import Hotpot
from hotpot.wrappers import Request

app = Hotpot()


@app.route("/")
def index(_app: Hotpot, request: Request):
    return {"index": True}


if __name__ == "__main__":
    # app will automatically run on localhost:8080
    app.run()
```

For more examples, please read the [Examples](https://github.com/RutaTang/Hotpot/tree/master/examples).

## Tutorial

In this tutorial, we will build a simple poll web.

## Document

**Note**: Only list a few useful and important API which might be enough to build a simple app.

### hotpot.app

#### hotpot.app.Hotpot(main_app=True,name="",base_rule="/")

_Parameters_:

1. **main_app**: describe whether app is the main app. If True, the app is main app, else, the app is not main app which
   will be combined to the main app, in order to make a whole app.
2. **name**: the name of the app, which is used for namespace of endpoints or view functions.
3. **base_rule**: default is "/", app's route rules will be built on base_rule.

_Functions_:

1. **combine_app(self, other_app: 'Hotpot')**:
    * _Description_: combine main app with other app to make a whole app.
    * _Parameters_:
        * **other_app**: other app which should not be main app.
    * _Return_: None

2. **run(self)**
    * _Description_: simple WSGI Server for development other than production.
    * _Return_: None

3. **add_config(self, config: Union[dict, str])**
    * _Description_: add a new config or cover the previous config.
    * _Parameters_:
        * **config**: can be a dict or the path of a config file which is formatted as ini file (e.g. config.ini).
    * _Return_: None

_Decorators_:

1. **route(self, rule, endpoint: str = None, \*\*options)**:
    * _Description_: map rule to endpoint (or say, view function).
    * _Parameters_:
        * **rule**: rule of route, e.g. "/"
        * **endpoint**: rule will be mapped to the endpoint, default is name of view function
    * _Return_: None
    * _Example_:
    ```python
    from hotpot import Hotpot
    app = Hotpot()
   
    @app.route("/")
    def index(_app,request):
        return {}
    ```
    * _Note_: view function (in the above example, it is the index function) must return a dict object or a Response


2. **view_exception_all(self)**:
    * _Description_: set custom view function for all http exceptions
    * _Return_: None
    * _Example_:
   ```python
    @app.view_exception_all()
    def view_exception_all(_app,error):
        if isinstance(error,NOT_FOUND):
             return JSONResponse({"Not_Found": 404})
        return JSONResponse({"": 000})
   ```

3. **view_exception_404(self)**:
    * _Description_: set view function for 404 http exception
    * _Return_: None
    * _Example_:
   ```python
   @app.view_exception_404()
   def view_exception_404(_app,error):
        return JSONResponse({"HttpException": 404})
   ```

_Life Circle Hook Decorators_:

You can use life circle hook decorators to process app,request, and response. For Example, you may use these hooks to
close database connection.

1. **after_app(self)**:
    * _Description_: will call functions decorated by this decorator when app.__del__ is called (or say when free app
      instance).
    * _Return_: None
    * _Example_:
   ```python
   @app.after_app()
   def after_app_f01(_app:Hotpot):
       _app.app_global.db.close()
   ```

2. **before_request(self)**:
    * _Description_: will call functions decorated by this decorator before each request is processed.
    * _Return_: None
    * _Example_:
   ```python
   @app.before_request()
   def before_request(_app: 'Hotpot'):
        _app.app_global.custom_variable = "hotpot"
   ```

3. **after_request(self)**:
    * _Description_: will call functions decorated by this decorator after each request is processed.
    * _Return_: None
    * _Example_:
   ```python
    @app.after_request()
    def after_request(_app, request) -> Request:
        print(_app.app_global.custom_variable)
        return request
   ```
    * _Note_: function decorated by this decorator must return an instance of **Request**

4. **before_response(self)**:
    * _Description_: will call functions decorated by this decorator before each response is processed.
    * _Return_: None
    * _Example_:
   ```python
    @app.before_response()
    def before_response(_app: 'Hotpot'):
        _app.app_global.custom_variable = "hotpot"
   ```

5. **after_response(self)**:
    * _Description_: will call functions decorated by this decorator after each response is processed.
    * _Return_: None
    * _Example_:
   ```python
    @app.after_response()
    def after_response(_app, request) -> Response:
        print(_app.app_global.custom_variable)
        return response
   ```
    * _Note_: function decorated by this decorator must return an instance of **Response**

### hotpot.sessions

#### hotpot.sessions.set_session(content: dict, response: ResponseBase, security_key: bytes)

_Parameters_:

1. **content**: content of cookie, e.g. content = {"uid","1"}
2. **response**: response of the request
3. **security_key**: the key to encrypt session data

_Return_: None

_Example_:

```python
@app.route("/login")
def login(_app: Hotpot, request: Request):
    response = JSONResponse({"Msg": "Successfully Log In!"})
    set_session({"name": "hotpot"}, response, security_key: _app.security_key)
    return response
```

#### hotpot.sessions.get_session(request: RequestBase, security_key: bytes)

_Parameters_:

1. **request**
2. **security_key**: the key to decrypt session data which must be same as security_key in set_session

_Return_: cookie data (type: dict)

_Example_:

```python
@app.route("/user_info")
def user_info(_app: Hotpot, request: Request):
    data = get_session(request, _app.security_key)
    print(data)
    return {}
```

#### hotpot.sessions.clear_session(response: ResponseBase)

_Parameters_:

1. **response**: response of the request

_Return_: None

_Example_:

```python
@app.route("/logout")
def logout(_app: Hotpot, request: Request):
    clear_session(request)
    return {"Msg": "Logout Successful"}
```

### hotpot.utils

#### hotpot.utils.generate_security_key():

_Return_: security_key

_Example_:

```python
app = Hotpot()
app.add_config(
    {
        "hostname": 'localhost',
        "port": 8080,
        "debug": True,
        "security_key": generate_security_key(),
    }
)
app.run()
```

#### hotpot.utils.redirect(location, code=302)

_Parameters_:

1. **location**
2. **code**

_Return_: Response

#### hotpot.utils.login(uid: str, response: ResponseBase, security_key: bytes)

_Description_: a simple login util which store uid(user id) in cookie with encryption

_Parameters_:

1. **uid**: user id which will be stored in cookie with encryption
2. **response**
3. **security_key**: will be used to encrypt data

_Return_: None

_Example_:

```python
@app.route("/login")
def login(_app: Hotpot, request: Request):
    uid = "1" # get from database, here is just for simple
    response = JSONResponse({"Msg": "Successfully Log In!"})
    login(uid,response,_app.security_key)
    return response
```

#### hotpot.utils.logout(response: ResponseBase)

_Description_: a simple logout util which will clear cookie whose name is 'hotpot'

_Parameters_:

_Return_: None

1. **response**

```python
@app.route("/logout")
def logout(_app: Hotpot, request: Request):
    response = JSONResponse({"Msg": "Successfully Log In!"})
    logout(response)
    return response
```

####  login_required(security_key: bytes, fail_redirect: ResponseBase)

_Description_: a simple login required **Decorator** which check whether there is a 'uid' in cookie

_Parameters_: 

1. **security_key**: used to decrypt data stored in cookie
2. **fail_redirect**: should be an instance of Response, e.g. redirect("/")

_Return_: None

_Example_:
```python
@app.route("/user_info")
def user_info(_app: Hotpot, request: Request):
    @login_required(security_key=_app.security_key, fail_redirect=redirect("/"))
    def wrap(_app: Hotpot, request):
        return {"name":"hotpot"}

    return wrap(_app, request)
```




