from appconf import AppConf
from django.conf import settings


class WebExAppConf(AppConf):
    CLIENT_ID = None
    CLIENT_SECRET = None
    TOKEN_TYPE = "Bearer"
    ACCESS_TOKEN = None
    REFRESH_TOKEN = None
    TOKEN_CACHE_KEY = "WEBEX-TOKEN"
    BASE_URL = "https://webexapis.com/v1/"

    class Meta:
        prefix = "webex"
