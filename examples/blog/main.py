from src.hotpot.app import Hotpot
from src.hotpot.wrappers import Request

from werkzeug.exceptions import NotFound

from app.models import db
from app.admin import app as admin_app
from app.blog import app as blog_app

app = Hotpot()
app.app_global.base_url = "http://" + app.config.get("hostname") + ":" + str(app.config.get("port"))
app.app_global.db = db

app.combine_app(blog_app)
app.combine_app(admin_app)

if __name__ == "__main__":
    app.run()
