from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView
from sullissivik.login.middleware import LoginManager
from sullissivik.login.nemid.nemid import NemId


class TestView(TemplateView):
    template_name = 'sullissiviknemidlogin/test.html'

    def get_context_data(self, **kwargs):
        context = {'cpr': self.request.user.cpr}
        context.update(**kwargs)
        return context


class Login(View):

    def __init__(self):
        super().__init__()
        self.config = settings.NEMID_CONNECT

    def get(self, request, *args, **kwargs):
        user = NemId.authenticate(request)
        if user.is_authenticated:
            return redirect(LoginManager.get_backpage(request))

        # Sullissivik redirects back here, so if login somehow fails (and we don't trust sullisivik to keep the user in that case), we re-check and direct back
        return redirect_to_login(
            request.build_absolute_uri(),
            self.config.get('login_url'),
            self.config.get('redirect_field')
        )


class Logout(View):

    def __init__(self):
        super().__init__()
        self.config = settings.NEMID_CONNECT

    def get(self, request):
        if 'user_info' in request.session:
            del request.session['user_info']
        if 'login_method' in request.session:
            del request.session['login_method']
        response = redirect('aka:index')
        response.delete_cookie(self.config['cookie_name'])
        return response
