import requests
from django.conf import settings


class Dafo(object):
    def lookup_cpr(self, cpr, raise_on_fail=True):
        if settings.DEBUG:
            return {
                "cprNummer": cpr,
                "fornavn": "Test",
                "efternavn": "Testersen",
                "civilstand": "U",
                "civilstandsdato": "2000-01-01",
                "statsborgerskab": 5100,
                "køn": "M",
                "far": "0101010101",
                "mor": "0202020202",
                "statuskode": 1,
                "statuskodedato": "2001-03-17",
                "tilflytningsdato": "2017-01-31",
                "myndighedskode": 746,
                "vejkode": 1234,
                "kommune": "Testkommune",
                "adresse": "Testvej 1",
                "postnummer": 1234,
                "bynavn": "Testby",
                "stedkode": 0,
                "landekode": "DK",
                "beskyttelsestyper": [],
                "adresseringsnavn": "Testersen,Test",
            }
        return self._pitu(
            cpr, "cpr", f"Lookup for cpr {cpr} failed" if raise_on_fail else None
        )

    def lookup_cvr(self, cvr, raise_on_fail=True):
        if settings.DEBUG:
            return {
                "source": "CVR",
                "cvrNummer": cvr,
                "navn": "Testdimser A/S",
                "forretningsområde": "Uoplyst",
                "statuskode": "AKTIV",
                "statuskodedato": "2020-01-01",
                "myndighedskode": 957,
                "kommune": "QEQQATA",
                "postboks": 123,
                "postnummer": 3911,
                "bynavn": "Sisimiut",
                "landekode": "GL",
            }
        return self._pitu(
            cvr, "cvr", f"Lookup for cvr {cvr} failed" if raise_on_fail else None
        )

    def lookup_cvr_by_cpr(self, cpr, raise_on_fail=True):
        if settings.DEBUG:
            return [12345678]
        return self._pitu(
            cpr,
            "cprcvr",
            f"Ownership lookup for cpr {cpr} failed" if raise_on_fail else None,
        )

    def _pitu(self, rest_path, service_name, exception_message):
        config = settings.DAFO_CONNECT
        if not config["enabled"]:
            return {}
        response = requests.get(
            "https://%s/restapi/%s" % (config["pitu-server"], rest_path),
            headers={
                "Uxp-Client": config["pitu-client"],
                "Uxp-Service": config["pitu-service"][service_name],
            },
            verify=config["pitu-certificate"],
            cert=(config["client-certificate"], config["private-key"]),
            timeout=15,
        )
        if response.status_code == 200:
            return response.json()
        elif exception_message is not None:
            raise Exception("%s: %s" % (exception_message, response.content))
