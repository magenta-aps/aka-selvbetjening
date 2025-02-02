# SPDX-FileCopyrightText: 2024 Magenta ApS <info@magenta.dk>
#
# SPDX-License-Identifier: MPL-2.0
import json
import os

from django.urls import reverse_lazy
from project.settings.base import DEBUG
from project.util import strtobool

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SERIALIZER = "aka.utils.AKAJSONSerializer"
SESSION_EXPIRE_SECONDS = int(os.environ.get("SESSION_EXPIRE_SECONDS") or 1800)
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_EXPIRE_CALLABLE = "aka.utils.session_timed_out"


# Sessions & cookies
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = True
if not DEBUG:
    CSRF_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_SAMESITE = "None"
X_FRAME_OPTIONS = "DENY"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
ALLOWED_HOSTS = json.loads(os.environ.get("ALLOWED_HOSTS", '["*"]'))

# Login
SAML = {
    "enabled": bool(strtobool(os.environ.get("SAML_ENABLED", "False"))),
    "debug": 1,
    "entityid": os.environ.get("SAML_SP_ENTITY_ID"),
    "idp_entity_id": os.environ.get("SAML_IDP_ENTITY_ID"),
    "name": os.environ.get("SAML_NAME") or "AKAP",
    "description": os.environ.get("SAML_DESCRIPTION") or "AKA Selvbetjening",
    "verify_ssl_cert": False,
    "metadata_remote": os.environ.get("SAML_IDP_METADATA"),
    "metadata_remote_container": os.environ.get("SAML_IDP_METADATA_CONTAINER"),
    "metadata": {"local": ["/var/cache/aka/idp_metadata.xml"]},  # IdP Metadata
    "service": {
        "sp": {
            "name": os.environ.get("SAML_NAME") or "AKAP",
            "hide_assertion_consumer_service": False,
            "endpoints": {
                "assertion_consumer_service": [
                    (
                        os.environ.get("SAML_SP_LOGIN_CALLBACK_URI"),
                        "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
                    )
                ],
                "single_logout_service": [
                    (
                        os.environ.get("SAML_SP_LOGOUT_CALLBACK_URI"),
                        "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                    ),
                ],
            },
            "required_attributes": [
                "https://data.gov.dk/model/core/specVersion",
                "https://data.gov.dk/concept/core/nsis/loa",
                "https://data.gov.dk/model/core/eid/professional/orgName",
                "https://data.gov.dk/model/core/eid/cprNumber",
                "https://data.gov.dk/model/core/eid/fullName",
            ],
            "optional_attributes": [
                "https://data.gov.dk/model/core/eid/professional/cvr",
            ],
            "name_id_format": [
                "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent",
            ],
            "signing_algorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
            "authn_requests_signed": True,
            "want_assertions_signed": True,
            "want_response_signed": False,
            "allow_unsolicited": True,
            "logout_responses_signed": True,
        }
    },
    "key_file": os.environ.get("SAML_SP_KEY"),
    "cert_file": os.environ.get("SAML_SP_CERTIFICATE"),
    "encryption_keypairs": [
        {
            "key_file": os.environ.get("SAML_SP_KEY"),
            "cert_file": os.environ.get("SAML_SP_CERTIFICATE"),
        },
    ],
    "xmlsec_binary": "/usr/bin/xmlsec1",
    "delete_tmpfiles": True,
    "organization": {
        "name": [("Skattestyrelsen", "da")],
        "display_name": ["Skattestyrelsen"],
        "url": [("https://nanoq.gl", "da")],
    },
    "contact_person": [
        {
            "given_name": os.environ["SAML_CONTACT_TECHNICAL_NAME"],
            "email_address": os.environ["SAML_CONTACT_TECHNICAL_EMAIL"],
            "type": "technical",
        },
        {
            "given_name": os.environ["SAML_CONTACT_SUPPORT_NAME"],
            "email_address": os.environ["SAML_CONTACT_SUPPORT_EMAIL"],
            "type": "support",
        },
    ],
    "preferred_binding": {
        "attribute_consuming_service": [
            "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
        ],
        "single_logout_service": [
            "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
        ],
    },
}
LOGIN_PROVIDER_CLASS = os.environ.get("LOGIN_PROVIDER_CLASS") or None
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"  # Where to go after logout
LOGIN_URL = "/login/"
LOGIN_NAMESPACE = (
    "login"  # Must match namespace given to django_mitid_auth.urls in project/urls.py
)
LOGIN_TIMEOUT_URL = reverse_lazy("aka:login-timeout")
LOGIN_REPEATED_URL = reverse_lazy("aka:login-repeat")
LOGIN_NO_CPRCVR_URL = reverse_lazy("aka:login-no-cprcvr")
LOGIN_ASSURANCE_LEVEL_URL = reverse_lazy("aka:login-assurance-level")
LOGIN_WHITELISTED_URLS = [
    # reverse('aka:index'),
    "/favicon.ico",
    reverse_lazy("aka:javascript-language-catalog", kwargs={"locale": "da"}),
    reverse_lazy("aka:javascript-language-catalog", kwargs={"locale": "kl"}),
    reverse_lazy("aka:set-language"),
    reverse_lazy("aka:downtime"),
    LOGIN_URL,
    LOGIN_TIMEOUT_URL,
    LOGIN_REPEATED_URL,
    LOGIN_NO_CPRCVR_URL,
    LOGIN_ASSURANCE_LEVEL_URL,
    reverse_lazy("metrics:health_check_storage"),
    reverse_lazy("metrics:health_check_database"),
    # Udbytte API
    reverse_lazy("udbytte:api-1.0.0:u1a_list"),
    reverse_lazy("udbytte:api-1.0.0:u1a_item_list"),
    reverse_lazy("udbytte:api-1.0.0:u1a_item_unique_cprs"),
]
MITID_TEST_ENABLED = bool(strtobool(os.environ.get("MITID_TEST_ENABLED", "False")))
DEFAULT_CPR = os.environ.get("DEFAULT_CPR", None)
DEFAULT_CVR = os.environ.get("DEFAULT_CVR", None)
LOGIN_BYPASS_ENABLED = bool(strtobool(os.environ.get("LOGIN_BYPASS_ENABLED", "False")))
POPULATE_DUMMY_SESSION = False
