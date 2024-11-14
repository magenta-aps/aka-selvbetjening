# SPDX-FileCopyrightText: 2024 Magenta ApS <info@magenta.dk>
#
# SPDX-License-Identifier: MPL-2.0
import os

from project.settings.base import get_file_contents
from project.util import strtobool

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
