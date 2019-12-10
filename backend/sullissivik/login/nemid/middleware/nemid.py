from django.contrib.auth.views import redirect_to_login
from django.urls import reverse_lazy
from django.conf import settings
from zeep import Client
from zeep.helpers import serialize_object

from backend.sullissivik.login.nemid.models import SessionOnlyUser


class LoggedIn:

    def __init__(self, get_response):
        self.config = settings.NEMID_CONNECT
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
        if request.path not in self.white_listed_urls and self.enabled is True:
            request.user = SessionOnlyUser.get_user(request.session)
            if not request.user.is_authenticated:
                request.user = self.authenticate(request)
                if request.user is not None and request.user.is_authenticated:
                    request.session['user_info'] = request.user.dict()
                else:
                    return self.handle_no_permission(request)
        return self.get_response(request)

    def authenticate(self, request):
        cookie = request.COOKIES.get(self.config.get('cookie_name'))
        if cookie is not None:
            client = Client(self.config.get('federation_service'))
            # Convert zeep object to OrderedDict
            user_data = serialize_object(client.service.GetUser(cookie))
            # federationPid = user_data.get('FederationPid')
            cpr = user_data.get('CPR')
            name = user_data.get('Name')
            is_authenticated = user_data.get('IsAuthenticated')
            if is_authenticated is not True:
                return None
            if cpr is None:
                return None
            return SessionOnlyUser.get_user(request.session, cpr, name)
        return None

    def handle_no_permission(self, request):
        # if self.raise_exception:
        #     raise PermissionDenied(self.get_permission_denied_message())
        return redirect_to_login(
            request.build_absolute_uri(),
            self.config.get('login_url'),
            self.config.get('redirect_field')
        )
