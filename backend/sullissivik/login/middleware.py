from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.http import urlencode, urlquote
from sullissivik.login.nemid.nemid import NemId
from sullissivik.login.openid.openid import OpenId


class LoginManager:

    @property
    def enabled(self):
        return NemId.enabled() or OpenId.enabled()

    white_listed_urls = []

    def __init__(self, get_response):
        self.get_response = get_response
        # Urls that should not redirect an anonymous user to login page
        self.white_listed_urls = NemId.whitelist + OpenId.whitelist + [
            # reverse('aka:index'),
            reverse('aka:login'),
            '/favicon.ico',
            reverse('aka:javascript-language-catalog', kwargs={'locale': 'da'}),
            reverse('aka:javascript-language-catalog', kwargs={'locale': 'kl'}),
            reverse('aka:set-language'),
            reverse('status')
        ]

    def redirect_to_login(self, request):
        backpage = urlquote(request.path)
        if request.GET:
            backpage += "?" + urlencode(request.GET, True)
        return redirect(reverse_lazy('aka:login') + "?back=" + backpage)

    def __call__(self, request):
        if self.enabled:
            # When any non-whitelisted page is loaded, check if we are authenticated

            if request.path not in self.white_listed_urls and request.path.rstrip('/') not in self.white_listed_urls and not request.path.startswith(settings.STATIC_URL):
                if 'user_info' not in request.session or not request.session['user_info']:
                    if not self.authenticate(request):  # The user might not have anything in his session, but he may have a cookie that can log him in anyway
                        return self.redirect_to_login(request)
        else:
            if 'user_info' not in request.session or not request.session['user_info']:
                request.session['user_info'] = {
                    'CVR': settings.DEFAULT_CVR,
                    'CPR': settings.DEFAULT_CPR,
                }
        try:
            response = self.get_response(request)
            if response.status_code == 403:
                return self.redirect_to_login(request)
            return response
        except PermissionDenied:
            return self.redirect_to_login(request)

    @staticmethod
    def authenticate(request):
        user = NemId.authenticate(request)
        return user is not None and user.is_authenticated

    @staticmethod
    def get_backpage(request):
        backpage = request.GET.get('back', request.session.get('backpage', reverse('aka:index')))
        return backpage
