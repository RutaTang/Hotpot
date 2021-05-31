
from src.hotpot import Hotpot, Request

from v1 import bp
from v1.models import engine

app = Hotpot(main_app=True)
app.app_global.engine = engine

app.combine_app(bp)

if __name__ == "__main__":
    app.run()