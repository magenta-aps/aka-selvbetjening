import os
import sys
from distutils.util import strtobool

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
SITE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SITE_DIR)
PROJECT_DIR = os.path.dirname(BASE_DIR)
AKA_DIR = os.path.join(BASE_DIR, "aka")
SHARED_DIR = os.path.join(PROJECT_DIR, "shared")

DEBUG = bool(strtobool(os.environ.get("DJANGO_DEBUG", "False")))
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
TIME_ZONE = os.environ.get("DJANGO_TIMEZONE", "America/Godthab")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
if not DEBUG:
    CSRF_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_SAMESITE = "None"
X_FRAME_OPTIONS = "DENY"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SERIALIZER = "aka.utils.AKAJSONSerializer"


MEDIA_URL = BASE_DIR + "/upload/"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ["POSTGRES_HOST"],
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {  # A flag to only log specified in production
            "()": "django.utils.log.RequireDebugFalse"
        },
        "require_debug_true": {  # A flag used for DEBUGGING only logs
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "verbose": {
            "format": "{name} {levelname} {asctime} {module} {funcName} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "encrypted": {
            "format": "\n%(asctime)s %(levelname)s %(name)s %(pathname)s:%(lineno)s    %(message)s",
            "()": "aka.encrypted_logging.EncryptedLogFormatterFactory",
        },
        "unencrypted": {
            "format": "\n%(asctime)s %(levelname)s %(name)s %(pathname)s:%(lineno)s    %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "stream": sys.stdout,
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "/var/log/aka/aka.log.asc",
            "when": "D",  # Roll log each day
            "formatter": "encrypted",
        },
        "unencrypted_file": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "/var/log/aka/aka.log",
            "when": "D",  # Roll log each day
            "formatter": "unencrypted",
        },
    },
    "loggers": {
        "zeep.transports": {
            "level": "DEBUG",
            "propagate": False,
            "handlers": ["file"],
        },
        "aka.clients.prisme": {
            "level": "DEBUG",
            "propagate": False,
            "handlers": ["file"],
        },
        "aka": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": True,
        },
        "oic": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}

ENCRYPTED_LOG_KEY_UID = "AKA Selvbetjening"

ALLOWED_HOSTS = ["*"]

AUTHENTICATION_BACKENDS = ["login.nemid.authentication.CookieAuthBackend"]

# See local_settings_example.py
SULLISSIVIK_FEDERATION_SERVICE = None

# Application definition

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.contrib.auth",
    "django_mitid_auth",
    "aka",
    "mitid_test",
    "watchman",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django_mitid_auth.middleware.LoginManager",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_session_timeout.middleware.SessionTimeoutMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"

LANGUAGE_CODE = "da-dk"
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGE_COOKIE_NAME = "Sullissivik.Portal.Lang"
LANGUAGE_COOKIE_DOMAIN = os.environ["DJANGO_LANGUAGE_COOKIE_DOMAIN"]
LOCALE_PATHS = [os.path.join(BASE_DIR, "i18n")]
LANGUAGES = [
    ("da", _("Danish")),
    ("kl", _("Greenlandic")),
]


LOCALE_MAP = {"da": "da-DK", "kl": "kl-GL"}

DEFAULT_CHARSET = "utf-8"

USE_THOUSAND_SEPARATOR = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(AKA_DIR, "static")
STATICFILES_DIRS = []


def get_file_contents(filename):
    with open(filename, "r") as f:
        return f.read()


PRISME_CONNECT = {
    "mock": bool(strtobool(os.environ.get("PRISME_MOCK", "False"))),
    "wsdl_file": os.environ.get("PRISME_WSDL", ""),
    "auth": {
        "basic": {
            "username": os.environ.get("PRISME_USERNAME", ""),
            "domain": os.environ.get("PRISME_DOMAIN", ""),
            "password": os.environ.get("PRISME_PASSWORD", ""),
        }
    },
    "mock_data": {
        "PrismeSELRequest": get_file_contents(
            "aka/mockdata/employeraccount_response.xml"
        ),
        "PrismeSELTotalRequest": get_file_contents(
            "aka/mockdata/employeraccount_total_response.xml"
        ),
        "PrismeAKIRequest": get_file_contents(
            "aka/mockdata/citizenaccount_response.xml"
        ),
        "PrismeInterestNoteRequest": get_file_contents(
            "aka/mockdata/interestnote_response.xml"
        ),
    },
}

DAFO_CONNECT = {
    "enabled": bool(strtobool(os.environ.get("DAFO_ENABLED", "True"))),
    "pitu-server": "10.240.76.4",
    "client-certificate": os.environ.get("DAFO_CERTIFICATE", ""),
    "private-key": os.environ.get("DAFO_KEY", ""),
    "pitu-certificate": os.environ.get("DAFO_CA_CERTIFICATE", ""),
    "pitu-client": "PITU/GOV/AKA/AKA_Selvbetjening",
    "pitu-service": {
        "cpr": "PITU/GOV/DIA/magenta_services/DAFO-PRISME-CPR-COMBINED/v1",
        "cvr": "PITU/GOV/DIA/magenta_services/DAFO-PRISME-CVR-COMBINED/v1",
        "cprcvr": "PITU/GOV/DIA/magenta_services/DAFO-CVR-OWNED-BY/v1",
    },
}

OPENID_CONNECT = {
    "enabled": bool(strtobool(os.environ.get("OPENID_ENABLED", "False"))),
    "issuer": os.environ.get(
        "OPENID_ISSUER", ""
    ),  # top level url to the issuer, used for autodiscovery
    "scope": os.environ.get(
        "OPENID_SCOPE", ""
    ),  # openid is mandatory to indicated is is a openid OP, we need to use digitalimik to get the cpr/cvr number.
    "client_id": os.environ.get(
        "OPENID_CLIENT_ID", ""
    ),  # id of the system (ouath), registered at headnet
    "client_certificate": os.environ.get(
        "OPENID_CERTIFICATE", ""
    ),  # path to client certificate used to secure the communication between the system and OP
    "private_key": os.environ.get(
        "OPENID_KEY", ""
    ),  # used for signing messages passed to the OP
    "redirect_uri": os.environ.get(
        "OPENID_REDIRECT_URI", ""
    ),  # url registered at headnet to redirect the user to after a successfull login at OP
    "logout_uri": os.environ.get(
        "OPENID_LOGOUT_URI", ""
    ),  # url registered at headnet to call when logging out, removing session data there
    "front_channel_logout_uri": os.environ.get(
        "OPENID_FRONT_LOGOUT_URI", ""
    ),  # url registered at headnet to call when logging out, should clear our cookies etc.
    "post_logout_redirect_uri": os.environ.get(
        "OPENID_POST_REDIRECT_URI", ""
    ),  # url registered at headnet to redirect to when logout is complete
}


def read_file(filename):
    if filename is not None:
        try:
            with open(filename, "r") as file:
                return file.read()
        except FileNotFoundError:
            pass
    return None


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "default_cache",
    },
    "saml": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "saml_cache",
    },
}

SAML = {
    "enabled": bool(strtobool(os.environ.get("SAML_ENABLED", "False"))),
    "debug": 1,
    "entityid": os.environ.get("SAML_SP_ENTITY_ID"),
    "idp_entity_id": os.environ.get("SAML_IDP_ENTITY_ID"),
    "name": "AKAP Test",
    "description": "AKAP Test",
    "verify_ssl_cert": False,
    "metadata": {  # IdP Metadata
        "remote": [{"url": os.environ.get("SAML_IDP_METADATA")}]
    },
    "service": {
        "sp": {
            "name": "AKAP Test",
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
            "authn_requests_signed": True,
            "want_assertions_signed": True,
            "want_response_signed": False,
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
            "allow_unsolicited": True,  # TODO: maybe False?
            "signing_algorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
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
        "name": [("AKAP Test", "da")],
        "display_name": ["AKAP Test"],
        "url": [("https://magenta.dk", "da")],
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
LOGIN_WHITELISTED_URLS = [
    # reverse('aka:index'),
    "/favicon.ico",
    reverse_lazy("aka:javascript-language-catalog", kwargs={"locale": "da"}),
    reverse_lazy("aka:javascript-language-catalog", kwargs={"locale": "kl"}),
    reverse_lazy("aka:set-language"),
    reverse_lazy("status"),
    LOGIN_URL,
]
MITID_TEST_ENABLED = bool(strtobool(os.environ.get("MITID_TEST_ENABLED", "False")))
SESSION_EXPIRE_SECONDS = int(os.environ.get("SESSION_EXPIRE_SECONDS") or 3600)
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True

MOUNTS = {
    "claimant_account_statements": {  # 6.5
        "maindir": "/tmp",
        "subdir": "{cvr}.*",
        "files": ".*",
    }
}

# Max 2 MB - can be lower if we want
MAX_UPLOAD_FILESIZE = 22097152

DEFAULT_CPR = os.environ.get("DEFAULT_CPR", None)
DEFAULT_CVR = os.environ.get("DEFAULT_CVR", None)
LOGIN_BYPASS_ENABLED = bool(strtobool(os.environ.get("LOGIN_BYPASS_ENABLED", "False")))

# Skip health_check for cache layer and storage since we are not using it
WATCHMAN_CHECKS = ("watchman.checks.databases",)
