from django.conf import settings
from django.urls import reverse
from django.utils.module_loading import import_string
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import View

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

LoginProvider = import_string(settings.LOGIN_PROVIDER_CLASS)


class LoginView(View):
    def get(self, request):
        provider = LoginProvider.from_settings()
        request.session['login_method'] = provider.name
        return provider.login(request)


@method_decorator(csrf_exempt, name='dispatch')
class LoginCallbackView(View):
    def get(self, request):
        provider = LoginProvider.from_settings()
        return provider.handle_login_callback(
            request=request,
            success_url=reverse('aka:index'),
            failure_url=reverse('saml-login')
        )

    def post(self, request, *args, **kwargs):
        provider = LoginProvider.from_settings()
        return provider.handle_login_callback(
            request=request,
            success_url=reverse('aka:index'),
            failure_url=reverse('saml-login')
        )


class LogoutView(View):
    def get(self, request):
        provider = LoginProvider.from_settings()
        return provider.logout(request)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutCallbackView(View):

    @xframe_options_exempt
    def get(self, request):
        provider = LoginProvider.from_settings()
        return provider.handle_logout_callback(request)

    def post(self, request, *args, **kwargs):
        provider = LoginProvider.from_settings()
        return provider.handle_logout_callback(request)


class MetadataView(View):
    def get(self, request):
        provider = LoginProvider.from_settings()
        return provider.metadata(request)

