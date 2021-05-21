class AppGlobal(dict):
    """
    Used as global namespace during app run
    can be used to:
    1. Store config
    2. connect db
    3. more as you can imagine

    Ex.
    app = Hotpot()
    Get app global: app.app_global
    Set app global: app.app_global.db = DB()
    """

    def __init__(self):
        super().__init__()

    def __getattribute__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

