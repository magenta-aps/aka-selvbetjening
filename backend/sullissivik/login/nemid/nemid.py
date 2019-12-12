from django.conf import settings
from django.urls import reverse_lazy
from sullissivik.login.nemid.models import SessionOnlyUser
from zeep import Client
from zeep.helpers import serialize_object


class NemId:

    @staticmethod
    def enabled():
        return settings.NEMID_CONNECT.get("enabled")

    @staticmethod
    def authenticate(request):
        user = SessionOnlyUser.get_user(request.session)
        if not user.is_authenticated:
            config = settings.NEMID_CONNECT
            cookie = request.COOKIES.get(config.get('cookie_name'))
            if cookie is not None:
                client = Client(config.get('federation_service'))
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
                user = request.user = SessionOnlyUser.get_user(request.session, cpr, name)
                if request.user.is_authenticated:
                    request.session['user_info'] = user.dict()
        return user

    whitelist = [reverse_lazy('nemid:login')]
