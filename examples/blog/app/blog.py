from src.hotpot.app import Hotpot
from src.hotpot.wrappers import Request

from werkzeug.exceptions import NotFound


app = Hotpot()


@app.route("/")
def index(_app: 'Hotpot', request: Request):
    articles = _app.app_global.db['articles']
    articles_url = []
    for _article in articles:
        articles_url.append(_app.app_global.base_url + "/article/" + str(_article['id']) + "/")
    return {"index": {"articles": articles_url}}


@app.route("/article/<int:id>/")
def article(_app: 'Hotpot', request: Request, id: int):
    articles = _app.app_global.db['articles']
    for _article in articles:
        if _article['id'] == id:
            return _article
    raise NotFound(f"Can not found the article with id={id}")
