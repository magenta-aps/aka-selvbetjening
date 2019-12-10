from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.views import View
from django.views.generic import TemplateView, RedirectView


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
        return redirect_to_login(
            request.build_absolute_uri(),
            self.config.get('login_url'),
            self.config.get('redirect_field')
        )
