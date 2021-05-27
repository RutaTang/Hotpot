# Hotpot
**A tiny and easy python web framework just for your fun! :)**

<div style="text-align: center">
<img src="https://github.com/RutaTang/Hotpot/blob/master/artworks/hotpot.png?raw=true" style="width: 150px;height: 150px;">
</div>

Hotpot is designed **almost** just for JSON RESTful, but for sure, you can render template or transform data with xml as you want.

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

#### hotpot.app.Hotpot(main_app=True,name="",base_rule="/")

_Parameters_:

1. **main_app**: describe whether app is the main app. If True, the app is main app, else, the app is not main app
   which will be combined to the main app, in order to make a whole app.
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
    * _Note_: view function (in the above example, it is the index function) must return a dict object
   or a Response
      

2. **view_exception_all(self)**:
   