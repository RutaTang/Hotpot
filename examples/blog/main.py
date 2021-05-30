from src.hotpot import Hotpot, Request
from v1 import app as v1_app

app = Hotpot(main_app=True)
app.combine_app(v1_app)

if __name__ == "__main__":
    app.run()