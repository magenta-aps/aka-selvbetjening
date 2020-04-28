import requests
from django.conf import settings


DEBUG = True


class Dafo(object):

    def __init__(self):
        self.login()

    def login(self):
        config = settings.DAFO_CONNECT
        response = requests.get(
            config['address']['token'].format(
                username=config['auth']['username'],
                password=config['auth']['password']
            )
        )
        if response.status_code == 200:
            self.token = response.text
        elif DEBUG:
            pass
        else:
            raise Exception("Login to DAFO failed")

    def lookup_cpr(self, cpr):
        if DEBUG:
            return {}
        config = settings.DAFO_CONNECT
        response = requests.get(
            config['address']['cpr'].format(cpr=cpr),
            headers={'Authorization': f"SAML {self.token}"},
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Lookup for cpr {cpr} failed")

    def lookup_cvr(self, cvr):
        if DEBUG:
            return {}
        config = settings.DAFO_CONNECT
        response = requests.get(
            config['address']['cvr'].format(cvr=cvr),
            headers={'Authorization': f"SAML {self.token}"},
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Lookup for cvr {cvr} failed")
