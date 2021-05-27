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

### hotpot.app.Hotpot(mian_app=True,)