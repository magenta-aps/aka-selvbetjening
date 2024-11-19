# SPDX-FileCopyrightText: 2024 Magenta ApS <info@magenta.dk>
#
# SPDX-License-Identifier: MPL-2.0
import os
from typing import Dict

from project.settings.base import ENVIRONMENT

# Logging
LOGGING: Dict = {
    "version": 1,
    "disable_existing_loggers": True,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "formatters": {
        "simple": {
            "format": "[{asctime}] [{levelname}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
    "loggers": {
        "zeep.transports": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        "aka.clients.prisme": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
        "aka": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
        "oic": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
        "django_mitid_auth": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
        "weasyprint": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "fontTools": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
log_filename = "/log/akap.log"
if os.path.isfile(log_filename) and ENVIRONMENT != "development":
    LOGGING["handlers"]["file"] = {
        "class": "logging.FileHandler",  # eller WatchedFileHandler
        "filename": log_filename,
        "formatter": "simple",
    }
    LOGGING["root"] = {
        "handlers": ["console", "file"],
        "level": "INFO",
    }
    for name, config in LOGGING["loggers"].items():
        config["handlers"].append("file")
