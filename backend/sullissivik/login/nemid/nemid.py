import sys
import traceback

from django.conf import settings
from django.urls import reverse_lazy
from requests import Session
from sullissivik.login.nemid.models import SessionOnlyUser
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.plugins import HistoryPlugin
from zeep.wsse import Signature


class NemId:

    @staticmethod
    def enabled():
        return settings.NEMID_CONNECT.get("enabled")

    @staticmethod
    def authenticate(request):
        user = SessionOnlyUser.get_user(request.session)
        if not user.is_authenticated:
            try:
                config = settings.NEMID_CONNECT
                cookie = request.COOKIES.get(config.get('cookie_name'))
                if cookie is not None:

                    session = Session()
                    session.cert = (
                        config['client_certificate'],
                        config['private_key']
                    )

                    client = Client(
                        config.get('federation_service'),
                        transport=Transport(
                            session=session
                        ),
                        # plugins=[HistoryPlugin()],
                        # wsse=Signature(
                        #     config['private_key'],
                        #     config['client_certificate']
                        # ),
                    )
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
            except Exception as e:
                print(e)
                exc_info = sys.exc_info()
                traceback.print_exception(*exc_info)
                raise e
        return user

    whitelist = [reverse_lazy('nemid:login')]

    @staticmethod
    def clear_session(session):
        for key in ['user_info', 'login_method']:
            if key in session:
                del session[key]

    @staticmethod
    def logout():
        response = redirect('aka:index')
        response.delete_cookie(settings.NEMID_CONNECT['cookie_name'])
        return response
