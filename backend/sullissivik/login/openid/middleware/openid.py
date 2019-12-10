from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.conf import settings


class LoggedIn:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.
        self.enabled = settings.OPENID_CONNECT.get('enabled', True)
        # urls we do not want to redirect from
        self.white_listed_urls = [reverse_lazy('openid:login'),
                                  reverse_lazy('openid:logout'),
                                  reverse_lazy('openid:callback'),
                                  reverse_lazy('nemid:test'),
                                  reverse_lazy('aka:login')]

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.path not in self.white_listed_urls and self.enabled is True:
            if 'user_info' not in request.session or not request.session['user_info']:
                return redirect('openid:login')

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
