import platform
DEV_SERVERS = [
    'COM02',
]

if platform.node() in DEV_SERVERS:
    from .development import *
else:
    from .production import *