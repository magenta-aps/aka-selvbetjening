# SPDX-FileCopyrightText: 2024 Magenta ApS <info@magenta.dk>
#
# SPDX-License-Identifier: MPL-2.0
import os

from django.utils.translation import gettext_lazy as _
from project.settings.base import BASE_DIR

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
TIME_ZONE = os.environ.get("DJANGO_TIMEZONE", None) or os.environ.get(
    "TZ", "America/Godthab"
)
LOCALE_MAP = {"da": "da-DK", "kl": "kl-GL"}
DEFAULT_CHARSET = "utf-8"
USE_THOUSAND_SEPARATOR = True
