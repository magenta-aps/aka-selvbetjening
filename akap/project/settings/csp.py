# SPDX-FileCopyrightText: 2024 Magenta ApS <info@magenta.dk>
#
# SPDX-License-Identifier: MPL-2.0
from project.settings.base import DEBUG

# django-csp
CSP_DEFAULT_SRC = (
    "'self'",
    "localhost:8000" if DEBUG else "https://akap.sullissivik.gl",
    "cdnjs.cloudflare.com",
    "cdn.datatables.net",
)
CSP_SCRIPT_SRC_ATTR = (
    "'self'",
    "localhost:8000" if DEBUG else "https://akap.sullissivik.gl",
    "code.jquery.com",
    "cdnjs.cloudflare.com",
    "cdn.datatables.net",
)
CSP_STYLE_SRC_ATTR = ("'self'",)
CSP_IMG_SRC = (
    "'self'",
    "data:",
    "www.sullissivik.gl",
)
