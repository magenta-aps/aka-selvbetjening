from django.urls import reverse_lazy
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from jwkest.jwk import rsa_load
from oic.oic import Client, rndstr
from oic.oic.message import RegistrationResponse
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from oic.utils.keyio import KeyBundle


class OpenId:

    open_id_settings = {}
    kc_rsa = None
    client_cert = None
    if getattr(settings, 'OPENID_CONNECT', None) and settings.OPENID_CONNECT.get('enabled', True):
        # if openID is enabled setup the key bundle and client_cert
        open_id_settings = settings.OPENID_CONNECT
        key = rsa_load(open_id_settings['private_key'])
        kc_rsa = KeyBundle([{'key': key, 'kty': 'RSA', 'use': 'ver'},
                            {'key': key, 'kty': 'RSA', 'use': 'sig'}])

        client_cert = (open_id_settings['client_certificate'], open_id_settings['private_key'])



    @staticmethod
    def enabled():
        return settings.OPENID_CONNECT.get('enabled', True)

    @staticmethod
    def authenticate(request):
        return None  # If the user has nothing in the session, we just don't log him in - there's no SSO cookie that we may want to check

    whitelist = [reverse_lazy('openid:login'), reverse_lazy('openid:callback'), reverse_lazy('openid:logout-callback')]

    @staticmethod
    def clear_session(session):
        for key in ['oid_state', 'oid_nonce', 'user_info', 'login_method']:
            if key in session:
                del session[key]


    @staticmethod
    def logout(session):
        client = Client(client_authn_method=CLIENT_AUTHN_METHOD, client_cert=OpenId.client_cert)
        client.store_registration_info(
            RegistrationResponse(**{
                'client_id': OpenId.open_id_settings['client_id'],
                'redirect_uris': [OpenId.open_id_settings['front_channel_logout_uri']]
            })
        )

        request_args = {
            # 'response_type': 'code',
            'scope': settings.OPENID_CONNECT['scope'],
            'client_id': settings.OPENID_CONNECT['client_id'],
            'redirect_uri': settings.OPENID_CONNECT['front_channel_logout_uri'],
            'state': rndstr(32),
            # 'nonce': rndstr(32)
        }
        auth_req = client.construct_EndSessionRequest(request_args=request_args, id_token=session['access_token_data']['id_token'])
        # logout_url = auth_req.request(client.end_session_endpoint)
        logout_url = auth_req.request(OpenId.open_id_settings['logout_uri']) # TODO: Gør dette pænere
        return HttpResponseRedirect(logout_url)

        # TODO: tjek at logoutcallback får rigtige data (tjek state og nonce osv), og redirect tilbage i det callback

        # This one will send a request from the server. It should be the client doing that
        # client.do_end_session_request(scope=settings.OPENID_CONNECT['scope'], state=rndstr(32))
