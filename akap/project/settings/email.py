# SPDX-FileCopyrightText: 2024 Magenta ApS <info@magenta.dk>
#
# SPDX-License-Identifier: MPL-2.0
import os

from project.util import strtobool

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", None)
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 25))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", None)
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", None)
EMAIL_USE_TLS = bool(strtobool(os.environ.get("EMAIL_USE_TLS", "False")))
EMAIL_USE_SSL = bool(strtobool(os.environ.get("EMAIL_USE_SSL", "False")))
EMAIL_SENDER = os.environ.get("EMAIL_SENDER", "noreply@nanoq.gl")
EMAIL_OFFICE_RECIPIENT = os.environ.get("EMAIL_OFFICE_RECIPIENT", "test@nanoq.gl")
EMAIL_OP_RECIPIENT = os.environ.get("EMAIL_OP_RECIPIENT", "pension@nanoq.gl")
