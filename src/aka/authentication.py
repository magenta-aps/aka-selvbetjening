from django.conf import settings
from zeep import Client
from zeep.helpers import serialize_object

from akasite.models import SessionOnlyUser


class CookieAuthBackend(object):
    """
    Authenticate users with a valid Sullissivik.Federation.Cookie.
    The data is provided by the SOAP webservice.
    """

    def authenticate(self, request):
        cookie = request.COOKIES.get('Sullissivik.Federation.Cookie')
        if cookie is not None:
            client = Client(settings.SULLISSIVIK_FEDERATION_SERVICE)
            # Convert zeep object to OrderedDict
            user_data = serialize_object(client.service.GetUser(cookie))
            # federationPid = user_data.get('FederationPid')
            cpr = user_data.get('CPR')
            name = user_data.get('Name')
            is_authenticated = user_data.get('IsAuthenticated')
            if is_authenticated is not True:
                print('Not authenticated')
                return None
            if cpr is None:
                print('Did not obtain CPR number')
                return None
            return SessionOnlyUser.get_user(request.session, cpr, name)
        return None
