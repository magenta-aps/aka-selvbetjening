import requests
from django.conf import settings

DEBUG = False


class Dafo(object):

    def lookup_cpr(self, cpr, raise_on_fail=True):
        return self._pitu(
            cpr,
            'cpr',
            f"Lookup for cpr {cpr} failed" if raise_on_fail else None
        )

    def lookup_cvr(self, cvr, raise_on_fail=True):
        return self._pitu(
            cvr,
            'cvr',
            f"Lookup for cvr {cvr} failed" if raise_on_fail else None
        )

    def lookup_cvr_by_cpr(self, cpr, raise_on_fail=True):
        return self._pitu(
            cpr,
            'cprcvr',
            f"Ownership lookup for cpr {cpr} failed" if raise_on_fail else None
        )

    def _pitu(self, rest_path, service_name, exception_message):
        if DEBUG:
            return {}
        config = settings.DAFO_CONNECT
        response = requests.get(
            "https://%s/restapi/%s" % (
                config['pitu-server'],
                rest_path
            ),
            headers={
                "Uxp-Client": config['pitu-client'],
                "Uxp-Service": config['pitu-service'][service_name],
            },
            verify=config['pitu-certificate'],
            cert=(config['client-certificate'], config['private-key']),
            timeout=15,
        )
        if response.status_code == 200:
            return response.json()
        elif exception_message is not None:
            raise Exception("%s: %s" % (exception_message, response.content))
