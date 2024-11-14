# SPDX-FileCopyrightText: 2024 Magenta ApS <info@magenta.dk>
#
# SPDX-License-Identifier: MPL-2.0
import os

from project.util import strtobool

DAFO_CONNECT = {
    "enabled": bool(strtobool(os.environ.get("DAFO_ENABLED", "True"))),
    "pitu-server": os.environ.get("PITU_SERVER", ""),
    "client-certificate": os.environ.get("PITU_CERTIFICATE", ""),
    "private-key": os.environ.get("PITU_KEY", ""),
    "pitu-certificate": os.environ.get("PITU_CA_CERTIFICATE", ""),
    "pitu-client": "PITU/GOV/AKA/AKA_Selvbetjening",
    "pitu-service": {
        "cpr": "PITU/GOV/DIA/magenta_services/DAFO-PRISME-CPR-COMBINED/v1",
        "cvr": "PITU/GOV/DIA/magenta_services/DAFO-PRISME-CVR-COMBINED/v1",
        "cprcvr": "PITU/GOV/DIA/magenta_services/DAFO-CVR-OWNED-BY/v1",
    },
}
