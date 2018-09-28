from django.contrib.auth import authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView

from akasite.models import SessionOnlyUser


class AuthenticateMixin(LoginRequiredMixin):

    redirect_field_name = 'returnurl'

    def dispatch(self, request, *args, **kwargs):
        request.user = SessionOnlyUser.get_user(request.session)
        if not request.user.is_authenticated:
            request.user = authenticate(request)
            if request.user is not None and request.user.is_authenticated:
                request.session['user'] = request.user.dict()
            else:
                return self.handle_no_permission()
        return super(AuthenticateMixin, self)\
            .dispatch(request, *args, **kwargs)

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return_url = self.request.build_absolute_uri()
        return redirect_to_login(
            return_url, self.get_login_url(), self.get_redirect_field_name()
        )


class TestView(AuthenticateMixin, TemplateView):
    template_name = 'akasite/test.html'

    def get_context_data(self, **kwargs):
        context = {'cpr': self.request.user.cpr}
        context.update(**kwargs)
        return context
