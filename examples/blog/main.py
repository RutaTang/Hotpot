from sqlalchemy import create_engine

from src.hotpot import Hotpot, Request
from v1 import bp

app = Hotpot(main_app=True)
app.app_global.engine = create_engine("mysql+pymysql://root:password@localhost:3306/test")

app.combine_app(bp)

if __name__ == "__main__":
    app.run()