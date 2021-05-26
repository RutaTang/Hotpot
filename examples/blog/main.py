from src.hotpot.app import Hotpot
from src.hotpot.wrappers import Request

from werkzeug.exceptions import NotFound

from app.models import db
from app.admin import app as admin_app

app = Hotpot()
app.app_global.base_url = "http://" + app.config.get("hostname") + ":" + str(app.config.get("port"))
app.app_global.db = db

app.combine_app(admin_app)


@app.route("/")
def index(_app: 'Hotpot', request: Request):
    articles = app.app_global.db['articles']
    articles_url = []
    for _article in articles:
        articles_url.append(app.app_global.base_url + "/article/" + str(_article['id']) + "/")
    return {"index": {"articles": articles_url}}


@app.route("/article/<int:id>/")
def article(_app: 'Hotpot', request: Request, id: int):
    articles = app.app_global.db['articles']
    for _article in articles:
        if _article['id'] == id:
            return _article
    raise NotFound(f"Can not found the article with id={id}")


if __name__ == "__main__":
    app.run()
