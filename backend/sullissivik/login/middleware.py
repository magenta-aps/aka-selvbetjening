from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.http import urlencode, urlquote


class LoginManager:

    @property
    def enabled(self):
        return settings.LOGIN_PROVIDER_CLASS is not None

    @property
    def login_provider_class(self):
        # LoginProvider is a class object defined in settings, e.g. aka.login.saml.OIOSaml
        return import_string(settings.LOGIN_PROVIDER_CLASS)

    white_listed_urls = []

    def __init__(self, get_response):
        if self.enabled:
            self.get_response = get_response
            # Urls that should not redirect an anonymous user to login page
            self.white_listed_urls = self.login_provider_class.whitelist + [
                # reverse('aka:index'),
                reverse('aka:login'),
                reverse('aka:logout'),
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
                if not self.login_provider_class.is_logged_in(request):
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
    def get_backpage(request):
        backpage = request.GET.get('back', request.session.get('backpage', reverse('aka:index')))
        return backpage
