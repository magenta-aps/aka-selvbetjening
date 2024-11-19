# SPDX-FileCopyrightText: 2024 Magenta ApS <info@magenta.dk>
#
# SPDX-License-Identifier: MPL-2.0
import json
import os
from decimal import Decimal

from project.util import strtobool

# Folders, debug, django secret
SITE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SITE_DIR)
PROJECT_DIR = os.path.dirname(BASE_DIR)
AKA_DIR = os.path.join(BASE_DIR, "aka")
SHARED_DIR = os.path.join(PROJECT_DIR, "shared")
DEBUG = bool(strtobool(os.environ.get("DJANGO_DEBUG", "False")))
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
VERSION = os.environ["COMMIT_TAG"]
ROOT_URLCONF = "project.urls"
WSGI_APPLICATION = "project.wsgi.application"
MEDIA_ROOT = "/upload/"  # Filesystem path to upload folder
HOST_DOMAIN = os.environ["HOST_DOMAIN"]
CSRF_TRUSTED_ORIGINS = [os.environ["HOST_DOMAIN"]]


# Prisme
def get_file_contents(filename):
    with open(filename, "r") as f:
        return f.read()


# Fixtures
MUNICIPALITIES = json.loads(os.environ.get("MUNICIPALITIES", "[]"))
# A basic fail-fast check
for municipality in MUNICIPALITIES:
    for expected in ("name", "code", "tax_percent"):
        if expected not in municipality:
            raise KeyError(expected)
    # Make it int or die trying
    municipality["code"] = int(municipality["code"])
    municipality["tax_percent"] = Decimal(municipality["tax_percent"])

TAX_FORM_U1 = os.environ.get(
    "TAX_FORM_U1", "http://etaxgps1/eTaxWebCitz1/Suliffinnut/Login.aspx"
)
TAX_FORM_STORAGE = os.path.join(MEDIA_ROOT, "u1")
