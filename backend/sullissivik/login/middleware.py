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
            reverse('aka:login'),
            '/favicon.ico',
            reverse('aka:javascript-language-catalog', kwargs={'locale': 'da'}),
            reverse('aka:javascript-language-catalog', kwargs={'locale': 'kl'}),
        ]

    def __call__(self, request):
        if self.enabled:
            # When any non-whitelisted page is loaded, check if we are authenticated
            if request.path not in self.white_listed_urls:
                print(request.path+" is not in "+str(self.white_listed_urls))
                if 'user_info' not in request.session or not request.session['user_info']:
                    if not self.authenticate(request):  # The user might not have anything in his session, but he may have a cookie that can log him in anyway
                        backpage = urlquote(request.path)
                        if request.GET:
                            backpage += "?" + urlencode(request.GET, True)
                        return redirect(reverse_lazy('aka:login') + "?back=" + backpage)
            else:
                print(request.path+" is in "+str(self.white_listed_urls))
        return self.get_response(request)

    @staticmethod
    def authenticate(request):
        user = NemId.authenticate(request)
        return user is not None and user.is_authenticated

    @staticmethod
    def get_backpage(request):
        backpage = request.GET.get('back', request.session.get('backpage', reverse('aka:index')))
        return backpage
