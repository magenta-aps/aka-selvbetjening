import base64
import logging

from django.conf import settings
from django.contrib import auth
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.urls import reverse_lazy
from django.utils.functional import cached_property
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from xmltodict import parse as xml_to_dict

logger = logging.getLogger(__name__)


class Saml2:
    """
    Borrows heavily from python3-saml-django
    https://pypi.org/project/python3-saml-django/

    We do this because we don't map logins to preexisting users in django, or even create users as they log in
    Instead we save their details (CPR, CVR etc.) in the session and clear the session on logout
    python3-saml-django couldn't do this for us, so we roll our own
    """
    def __init__(self, **settings):
        self.settings = settings

    whitelist = [
        reverse_lazy('aka:login-callback'),
        reverse_lazy('aka:logout-callback'),
        reverse_lazy('aka:metadata')
    ]

    @property
    def name(self):
        return 'saml2'

    session_keys = ('saml')

    @classmethod
    def from_settings(cls):
        return cls(**settings.SAML)

    claims_map = {
        'PersonName': 'http://schemas.microsoft.com/identity/claims/displayname',
    }

    @staticmethod
    def is_logged_in(request):
        return 'saml' in request.session

    @staticmethod
    def _clear_secrets(session):
        for key in Saml2.session_keys:
            if key in session:
                del session[key]

    @cached_property
    def onelogin_settings(self):
        return OneLogin_Saml2_Settings(self.settings, self.settings['base_directory'])

    def login(self, request):
        """Kick off a SAML login request."""
        req = self._prepare_django_request(request)
        saml_auth = OneLogin_Saml2_Auth(req, old_settings=self.onelogin_settings)
        if 'back' in request.GET:
            redirect_to = OneLogin_Saml2_Utils.get_self_url(req) + request.GET['back']
        else:
            redirect_to = OneLogin_Saml2_Utils.get_self_url(req) + self.settings['login_redirect']
        url = saml_auth.login(redirect_to)
        request.session['AuthNRequestID'] = saml_auth.get_last_request_id()
        return HttpResponseRedirect(url)

    def convert_saml_claims(self, saml_claims):
        return {
            key: saml_claims[claimKey][0]
            for key, claimKey in self.claims_map.items()
            if claimKey in saml_claims
        }

    def log_login(self, request, saml_auth, saml_claims):
        status = "failed" if saml_auth.get_errors() else "successful"
        log_dict = self.get_log_dict(request, saml_auth, saml_claims)
        logger.info(f"SAML Login {status}: {str(log_dict)}")

    def log_logout(self, request, saml_auth, saml_claims):
        status = "failed" if saml_auth.get_errors() else "successful"
        log_dict = self.get_log_dict(request, saml_auth, saml_claims)
        logger.info(f"SAML Logout {status}: {str(log_dict)}")

    def get_log_dict(self, request, saml_auth, saml_claims=None):
        return {
            'ResponseID': saml_auth.get_last_message_id(),
            'AssertionID': saml_auth.get_last_assertion_id(),
            'InResponseTo': saml_auth.get_last_response_in_response_to(),
            'Errors': saml_auth.get_errors(),
            'ErrorReason': saml_auth.get_last_error_reason(),
            'SubjectNameID': saml_auth.get_nameid(),
            'DjangoSessionID': request.session.session_key,
        }

    def handle_login_callback(self, request, success_url, failure_url):
        """Handle an AuthenticationResponse from the IdP."""
        if request.method != 'POST':
            return HttpResponse('Method not allowed.', status=405)
        try:
            req = self._prepare_django_request(request)
            saml_auth = OneLogin_Saml2_Auth(req, old_settings=self.onelogin_settings)

            request_id = request.session.get('AuthNRequestID', None)
            saml_auth.process_response(request_id=request_id)

            errors = saml_auth.get_errors()
            saml_claims = self.convert_saml_claims(saml_auth.get_attributes())  # empty dict if there are errors

            self.log_login(request, saml_auth, saml_claims)
            if not errors:
                request.session['saml'] = {
                    'nameId': saml_auth.get_nameid(),
                    'nameIdFormat': saml_auth.get_nameid_format(),
                    'nameIdNameQualifier': saml_auth.get_nameid_nq(),
                    'nameIdSPNameQualifier': saml_auth.get_nameid_spnq(),
                    'sessionIndex': saml_auth.get_session_index(),
                }
                request.session['user_info'] = saml_claims
                request.session['cvr'] = request.session['user_info'].get('CVR')

                # This data is used during Single Log Out
                if 'RelayState' in req['post_data'] \
                        and OneLogin_Saml2_Utils.get_self_url(req) != req['post_data']['RelayState']:
                    url = saml_auth.redirect_to(req['post_data']['RelayState'])
                    return HttpResponseRedirect(url)
                else:
                    return HttpResponseRedirect(success_url)
            logger.exception(saml_auth.get_last_error_reason())
            return HttpResponse(content="Invalid Response", status=400)
        except PermissionDenied:
            raise
        except Exception as e:
            logger.exception(e)
            return HttpResponse(content="Invalid Response", status=400)

    def logout(self, request):
        """Kick off a SAML logout request."""
        req = self._prepare_django_request(request)
        saml_auth = OneLogin_Saml2_Auth(req, old_settings=self.onelogin_settings)
        (name_id, session_index, name_id_format, name_id_nq, name_id_spnq) = (None, None, None, None, None)
        saml_session = request.session.get('saml', None)
        if saml_session:
            name_id = saml_session.get('nameId', None)
            session_index = saml_session.get('sessionIndex', None)
            name_id_format = saml_session.get('nameIdFormat', None)
            name_id_nq = saml_session.get('nameIdNameQualifier', None)
            name_id_spnq = saml_session.get('nameIdSPNameQualifier', None)
        url = saml_auth.logout(
            name_id=name_id, session_index=session_index, nq=name_id_nq, name_id_format=name_id_format, spnq=name_id_spnq,
            return_to=OneLogin_Saml2_Utils.get_self_url(req) + self.settings['logout_redirect']
        )
        request.session['LogoutRequestID'] = saml_auth.get_last_request_id()
        return HttpResponseRedirect(url)

    def handle_logout_callback(self, request):
        """Handle a LogoutResponse from the IdP."""
        if request.method != 'GET':
            return HttpResponse('Method not allowed.', status=405)
        req = self._prepare_django_request(request)
        saml_auth = OneLogin_Saml2_Auth(req, old_settings=self.onelogin_settings)
        request_id = request.session.get('LogoutRequestID', None)
        try:
            saml_claims = request.session.get('user_info')
            url = saml_auth.process_slo(request_id=request_id, delete_session_cb=lambda: request.session.flush())
            errors = saml_auth.get_errors()
            self.log_logout(request, saml_auth, saml_claims)
            if not errors:
                auth.logout(request)
                for key in ('user_info', 'cvr', 'cpr', 'saml'):
                    if key in request.session:
                        del request.session[key]
                redirect_to = url or self.settings['logout_redirect']
                return HttpResponseRedirect(redirect_to)
            else:
                logger.exception(saml_auth.get_last_error_reason())
                return HttpResponse("Invalid request", status=400)
        except UnicodeDecodeError:
            # Happens when someone messes with the response in the URL.  No need to log an exception.
            return HttpResponse("Invalid request - Unable to decode response", status=400)
        except Exception as e:
            logger.exception(e)
            return HttpResponse("Invalid request", status=400)

    def metadata(self, request):
        """Render the metadata of this service."""
        metadata_dict = self.onelogin_settings.get_sp_metadata()
        errors = self.onelogin_settings.validate_metadata(metadata_dict)
        if len(errors) == 0:
            resp = HttpResponse(content=metadata_dict, content_type='text/xml')
        else:
            resp = HttpResponseServerError(content=', '.join(errors))
        return resp

    def _prepare_django_request(self, request):
        """Extract data from a Django request in the way that OneLogin expects."""
        result = {
            'https': 'on' if request.is_secure() else 'off',
            'http_host': request.META.get('HTTP_HOST', '127.0.0.1'),
            'script_name': request.META['PATH_INFO'],
            'server_port': request.META['SERVER_PORT'],
            'get_data': request.GET.copy(),
            'post_data': request.POST.copy()
        }
        if self.settings['destination_host'] is not None:
            result['http_host'] = self.settings['destination_host']
        if self.settings['destination_https'] is not None:
            result['https'] = self.settings['destination_https']
            result['server_port'] = '443' if result['https'] else '80'
        if self.settings['destination_port'] is not None:
            result['server_port'] = self.settings['destination_port']
        return result


class OIOSaml(Saml2):

    @property
    def name(self):
        return 'oiosaml'

    """
    Maps session['user_info'] keys to SAML claims
    See spec at
    https://www.digitaliser.dk/resource/4390927/artefact/OIOSAMLWebSSOprofile3.0.pdf?artefact=true&PID=4904569
    """
    claims_map = {
        'SpecVer': 'https://data.gov.dk/model/core/specVersion',
        'BootstrapToken': 'https://data.gov.dk/model/core/eid/bootstrapToken',
        'Privilege': 'https://data.gov.dk/model/core/eid/privilegesIntermediate',
        'LevelOfAssurance': 'https://data.gov.dk/concept/core/nsis/loa',
        'IdentityAssuranceLevel': 'https://data.gov.dk/concept/core/nsis/ial',
        'AuthenticationAssuranceLevel': 'https://data.gov.dk/concept/core/nsis/aal',
        'Fullname': 'https://data.gov.dk/model/core/eid/fullName',
        'Firstname': 'https://data.gov.dk/model/core/eid/firstName',
        'Lastname': 'https://data.gov.dk/model/core/eid/lastName',
        'Alias': 'https://data.gov.dk/model/core/eid/alias',
        'Email': 'https://data.gov.dk/model/core/eid/email',
        'Age': 'https://data.gov.dk/model/core/eid/age',
        'CprUUID': 'https://data.gov.dk/model/core/eid/cprUuid',
        'CVR': 'https://data.gov.dk/model/core/eid/professional/cvr',
        'CPR': 'https://data.gov.dk/model/core/eid/cprNumber',
        'PersonName': 'https://data.gov.dk/model/core/eid/fullName',
        'OrganizationName': 'https://data.gov.dk/model/core/eid/professional/orgName',
    }

    @staticmethod
    def get_privileges(saml_claims):
        """
        Decode privileges claim as specified in
        https://digitaliser.dk/resource/2377872/artefact/OIOSAMLBasicPrivilegeProfile1_0_1.pdf?artefact=true&PID=2377876
        section 3.5
        """
        privileges_base64 = saml_claims.get('Privilege')
        if privileges_base64:
            privileges_xml = base64.b64decode(privileges_base64)
            privileges_dict = xml_to_dict(privileges_xml)
            return privileges_dict
        return None

    def get_log_dict(self, request, saml_auth, saml_claims=None):
        if saml_claims is None:
            saml_claims = {}
        return {
            **super().get_log_dict(request, saml_auth, saml_claims),
            'CPR': saml_claims.get('CPR'),
            'CVR': saml_claims.get('CVR'),
            'LevelOfAssurance': saml_claims.get('LevelOfAssurance'),
            'Privileges': self.get_privileges(saml_claims),
        }
