from oic.oic import Client, RegistrationResponse
from oic import rndstr
from oic.utils.http_util import Redirect
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from django.conf import settings
open_id_settings = settings.OPENID_CONNECT


def run():
    client_cert = (open_id_settings['client_certificate'], open_id_settings['private_key'])
    client = Client(client_authn_method=CLIENT_AUTHN_METHOD, client_cert=client_cert)
    provider_info = client.provider_config(open_id_settings['issuer'])
    print(provider_info)
    client_reg = RegistrationResponse(**{'client_id': open_id_settings['client_id'], 'redirect_uris': [open_id_settings['redirect_uri']]})
    client.store_registration_info(client_reg)

    print(client.authorization_endpoint)
    session = {}
    session["state"] = rndstr()
    session["nonce"] = rndstr()
    args = {
        "client_id": client.client_id,
        "response_type": "code",
        "scope": ["openid"],
        "nonce": session["nonce"],
        "redirect_uri": 'test', #client.registration_response["redirect_uris"][0],
        "state": session["state"]
    }

    auth_req = client.construct_AuthorizationRequest(request_args=args)

    login_url = auth_req.request(client.authorization_endpoint)
    print(login_url)
    print(Redirect(login_url))



if __name__ =="__main__":
    run()