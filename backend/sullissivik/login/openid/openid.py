from django.conf import settings
from django.urls import reverse_lazy


class OpenId:

    @staticmethod
    def enabled():
        return settings.OPENID_CONNECT.get('enabled', True)

    @staticmethod
    def authenticate(request):
        return None  # If the user has nothing in the session, we just don't log him in - there's no SSO cookie that we may want to check

    whitelist = [reverse_lazy('openid:login'), reverse_lazy('openid:logout'), reverse_lazy('openid:callback')]
