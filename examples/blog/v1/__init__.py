from src.hotpot import Hotpot, Request
from .views import bp

app = Hotpot(base_rule="/v1/")

app.combine_app(bp)