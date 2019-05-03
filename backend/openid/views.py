from urllib.parse import urlencode

from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from oic.oauth2 import ErrorResponse
from oic.oic import Client, rndstr
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from django.conf import settings
from oic.oic.message import AuthorizationResponse, RegistrationResponse
from django.views.decorators.clickjacking import xframe_options_exempt
open_id_settings = settings.OPENID_CONNECT


class Login(View):
    """
    builds up the url with the correct GET parameters and redirects the browser to it.
    So the user can login to the external OpenId Provider
    """
    http_method_names = ['get']

    def get(self, request):
        client_cert = (open_id_settings['client_certificate'], open_id_settings['private_key'])
        client = Client(client_authn_method=CLIENT_AUTHN_METHOD, client_cert=client_cert)
        provider_info = client.provider_config(open_id_settings['issuer'])
        client_reg = RegistrationResponse(**{'client_id': open_id_settings['client_id'], 'redirect_uris': [open_id_settings['redirect_uri']]})
        client.store_registration_info(client_reg)

        state = rndstr(32)
        nonce = rndstr(32)
        args = {'response_type': 'code',
                'scope': settings.OPENID_CONNECT['scope'],
                'client_id': settings.OPENID_CONNECT['client_id'],
                'redirect_uri': settings.OPENID_CONNECT['redirect_uri'],
                'state': state,
                'nonce': nonce}

        request.session['oid_state'] = state
        request.session['oid_nonce'] = nonce
        auth_req = client.construct_AuthorizationRequest(request_args=args)
        login_url = auth_req.request(client.authorization_endpoint)
        return HttpResponseRedirect(login_url)


class Callback(View):
    http_method_names = ['get']

    def get(self, request):
        if 'oid_state' not in request.session:
            msg = 'Session `oid_state` does not exist!'
            raise SuspiciousOperation(msg)

        nonce = request.session.get('oid_nonce')
        if nonce:
            # Make sure that nonce is not used twice
            del request.session['oid_nonce']

        client_cert = (settings.OPENID_CONNECT['client_certificate'], settings.OPENID_CONNECT['private_key'])
        client = Client(client_authn_method=CLIENT_AUTHN_METHOD, client_cert=client_cert)

        client_configuration = {'client_id': settings.OPENID_CONNECT['client_id'],
                                'token_endpoint_auth_method': 'private_key_jwt'}

        client.store_registration_info(client_configuration)

        aresp = client.parse_response(AuthorizationResponse, info=request.META['QUERY_STRING'], sformat="urlencoded")
        if isinstance(aresp, ErrorResponse):
            # we got an error from the OP
            # TODO and remove stuff from the session
            return HttpResponseRedirect(reverse('error'))  # TODO figure out how to add the error

        else:
            # we got a valid response
            if aresp['state'] != request.session['oid_state']:
                msg = 'Session `oid_state` does not match the OID callback state'
                # TODO and remove stuff from the session
                raise SuspiciousOperation(msg)

            provider_info = client.provider_config(settings.OPENID_CONNECT['issuer'])# TODO is this needed?

            request_args = {'code': aresp['code'],
                            'redirect_uri': request.build_absolute_uri(reverse('openid:callback'))}
            # this just needs to be the same as the previous callback

            resp = client.do_access_token_request(state=aresp['state'],
                                                  scope=settings.OPENID_CONNECT['scope'],
                                                  request_args=request_args
                                                  #authn_method="client_secret_jwt",
                                                  )

            print(resp)
            if isinstance(aresp, ErrorResponse):
                return HttpResponseRedirect(reverse('error'))
                # TODO figure out where we should redirect to when errors occur
            else:
                userinfo = client.do_user_info_request(state=aresp["state"]) #TODO i think this is just a stub
                # TODO set some variables in the session to indicate the user is loggedin
                print(userinfo)
                #TODO redirect to vue.js app


class Logout(View):

    @xframe_options_exempt
    def get(self, request):
        print(request.GET)
        print(request)
        return

class ErrorPage(TemplateView):
    pass