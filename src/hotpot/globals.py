from werkzeug.local import Local, LocalProxy, release_local

# thread-safe local globals
_local = Local()
g = _local('g')
request = _local('request')
current_app = _local('current_app')
