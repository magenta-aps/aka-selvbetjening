import base64
import datetime
import json
import logging
import os
from dataclasses import dataclass, field
from dateutil import parser as datetimeparser
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.files import File
from django.core.mail import EmailMultiAlternatives
from django.core.serializers.json import DjangoJSONEncoder
from django.core.signing import JSONSerializer
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django_mitid_auth.middleware import LoginManager
from math import floor
from typing import Any, List, Tuple
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration

logger = logging.getLogger(__name__)


def datefromstring(datestring):
    """
    Convert a string of the form YYYY-MM-DD to a datetime object.

    E.g. 20180203 is OK. 2018218 is not OK.

    :param datestring: Date in the form 'YYYY-MM-DD'.
    :type datestring: String
    :returns: datetime object.
    """

    return datetime.datetime.strptime(datestring, "%Y-%m-%d")


def datetostring(date):
    """
    Convert a date object to a string of the form YYYY-MM-DD.

    E.g. 20180203 is OK. 2018218 is not OK.

    :param datestring: Date in the form 'YYYY-MM-DD'.
    :type datestring: String
    :returns: datetime object.
    """

    return datetime.datetime.strftime(date, "%Y-%m-%d")


def get_file_contents(filename):
    with open(filename, "r") as f:
        return f.read()


def get_file_contents_base64(file):
    with file.open("rb") as fp:
        data = fp.read()
        return base64.b64encode(data).decode("ascii")


def getSharedJson(fileName):
    """
    This function generates a json(can be used as a dict)
    from a file shared between the frontend and backend.
    The file must be in a valid json format.

    """
    file_path = os.path.join(settings.SHARED_DIR, fileName)
    with open(file_path, "r", encoding="utf8") as jsonfile:
        return json.loads(jsonfile.read())


def get_ordereddict_key_index(ordereddict, key):
    for index, k in enumerate(ordereddict):
        if k == key:
            return index
    raise ValueError


def spreadsheet_col_letter(col_index):
    if col_index is None:
        return None
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    length = len(alphabet)
    if col_index >= length:
        return (
            spreadsheet_col_letter(floor(col_index / 26) - 1)
            + alphabet[col_index % length]
        )
    return alphabet[col_index]


def format_filesize(bytes, digits=1, SI=True):
    stepsize = 1000 if SI else 1024
    now = 1
    next = stepsize
    for step in ["", "k", "M", "G", "T", "P", "E", "Z", "Y"]:
        if bytes < next:
            if step:
                return ("{0:.%df} %s%sB" % (digits, step, "" if SI else "i")).format(
                    bytes / now
                )
            return "%d B" % bytes
        now = next
        next *= stepsize


def list_lstrip(lst, strip=None):
    lst = lst.copy()  # Work on a copy of the list
    while lst and lst[0] == strip:
        lst = lst[1:]
    return lst


def list_rstrip(lst, strip=None):
    lst = lst.copy()  # Work on a copy of the list
    while lst and lst[-1] == strip:
        lst = lst[:-1]
    return lst


def list_strip(lst, strip=None):
    return list_rstrip(list_lstrip(lst, strip), strip)


def dummy_management_form(
    name, total_forms=1, initial_forms=1, min_forms=1, max_forms=1000
):
    return {
        "%s-TOTAL_FORMS" % name: total_forms,
        "%s-INITIAL_FORMS" % name: initial_forms,
        "%s-MIN_NUM_FORMS" % name: min_forms,
        "%s-MAX_NUM_FORMS" % name: max_forms,
    }


def flatten(lst):
    if type(lst) is list:
        combined = []
        for x in lst:
            if type(x) is list:
                combined.extend(flatten(x))
            else:
                combined.append(x)
        return combined
    return [lst]


class LenientJsonSerializer(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, (File,)):
            return {"__type__": obj.__class__.__name__}
        return super().default(obj)


# Solves the issue where a datetime object and a string with an iso-encoded datetime will be serialized to the same json string,
# and deserialized to the same object. When we care about the type of the deserialized object, we add the information about the
# original class here. This is especially relevant if the user inputs a parseable datestring which is then rendered in a template.
class AKAJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return {"__datetime__": obj.isoformat()}
        if isinstance(obj, datetime.date):
            return {"__date__": obj.isoformat()}
        if isinstance(obj, Decimal):
            return {"__decimal__": str(obj)}
        return super().default(obj)


class AKAJSONSerializer(JSONSerializer):
    def dumps(self, obj):
        return json.dumps(obj, separators=(",", ":"), cls=AKAJSONEncoder).encode(
            "utf-8"
        )

    def loads(self, jsonstr, **kwargs):
        obj = super().loads(jsonstr, **kwargs)
        self.traverse(obj)
        return obj

    # convert strings that look like dates and datetimes to those classes
    def traverse(self, item):
        if isinstance(item, dict):
            if "__datetime__" in item:
                return datetimeparser.isoparse(item["__datetime__"])
            if "__date__" in item:
                return datetimeparser.isoparse(item["__date__"]).date()
            if "__decimal__" in item:
                return Decimal(item["__decimal__"])
            for k, v in item.items():
                changed_value = self.traverse(v)
                if changed_value is not None:
                    item[k] = changed_value
        elif isinstance(item, list):
            for i, v in enumerate(item):
                changed_value = self.traverse(v)
                if changed_value is not None:
                    item[i] = changed_value
        return None


def render_pdf(template_name, context, html_modifier=None):
    html = render_to_string(template_name, context)
    if callable(html_modifier):
        html = html_modifier(html)
    font_config = FontConfiguration()
    return HTML(string=html).write_pdf(font_config=font_config)


months = (
    _("January"),
    _("February"),
    _("March"),
    _("April"),
    _("May"),
    _("June"),
    _("July"),
    _("August"),
    _("September"),
    _("October"),
    _("November"),
    _("December"),
)


def month_name(month_number):
    return months[month_number - 1]


def chunks(lst, size):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), size):
        yield lst[i : i + size], i


@dataclass
class Field:
    name: str
    klass: str = "nb"
    title: str = None
    transkey: str = None
    labelkey: str = None
    modifier: callable = None
    number: bool = False
    boolean: bool = False

    @property
    def label(self):
        return self.labelkey or self.name


@dataclass
class Cell:
    field: Field
    value: Any


@dataclass
class Row:
    cells: List[Cell] = field(default_factory=list)


@dataclass
class Table:
    fields: List[Field] = field(default_factory=list)
    rows: List[Row] = field(default_factory=list)
    name: str = None
    total: dict = None


def session_timed_out(request):
    # What to do when session has timed out
    # See https://github.com/Lapeth/django-session-timeout
    whitelist = LoginManager.get_whitelisted_urls()
    if request.path in whitelist:
        return None
    redirect_url = getattr(settings, "SESSION_TIMEOUT_REDIRECT", None)
    if redirect_url:
        return redirect(redirect_url)
    else:
        return redirect_to_login(next=request.path)


def send_mail(
    recipient,
    subject,
    textbody,
    htmlbody=None,
    attachments: List[Tuple[str, bytes, str]] = None,
):
    if type(recipient) not in (list, tuple):
        recipient = (recipient,)
    message = EmailMultiAlternatives(
        subject=subject, body=textbody, from_email=settings.EMAIL_SENDER, to=recipient
    )
    if htmlbody:
        message.attach_alternative(htmlbody, "text/html")
    if attachments:
        for attachment in attachments:
            message.attach(*attachment)
    message.send()


def gettext_lang(language, string):
    with translation.override(language):
        return translation.gettext(string)
