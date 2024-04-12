import json as jsonlib
import locale
import re
from html import unescape
from urllib.parse import quote

from aka.utils import LenientJsonSerializer
from aka.utils import month_name as util_month_name
from django.template.defaultfilters import register
from django.utils.translation import gettext

trans_re = re.compile("_\\((.*)\\)")
format_re = re.compile("{(.*)}")

locale.setlocale(locale.LC_ALL, "")


@register.filter
def split(text, filter):
    return text.split(filter)


@register.filter
def json(data):
    return jsonlib.dumps(data, cls=LenientJsonSerializer)


@register.filter
def format(text, params):
    text = gettext(text)
    if params:
        if isinstance(params, str):
            params = jsonlib.loads(params)
        for key in params:
            value = params[key]
            if type(value) is tuple:
                # If a value is a tuple, it must be (message:string, params:dict,)
                value = format(value[0], value[1])
            else:
                value = format(str(value), None)
            text = text.replace("{" + key + "}", value)
            text = text.replace("%(" + key + ")s", value)
    return unescape(text)


@register.filter
def analyze(data):
    print("Analysis:")
    print("---------")
    print(type(data))
    print(dir(data))
    print(data)
    print("---------")
    return ""


@register.filter
def startswith(text, prefix):
    return type(text) is str and text.startswith(prefix)


@register.filter
def addstr(arg1, arg2):
    return "".join([str(a) if a is not None else "" for a in [arg1, arg2]])


@register.filter
def back(url, backurl):
    if backurl:
        return "".join([url, "&" if "?" in url else "?", "back=", quote(backurl)])
    return url


@register.filter
def urlparam(url, param):
    if param:
        (key, value) = param.split("=")
        return "".join([url, "&" if "?" in url else "?", key, "=", quote(value)])
    return url


@register.filter
def get(item, attribute):
    if hasattr(item, attribute):
        return getattr(item, attribute)
    if hasattr(item, "get"):
        return item.get(attribute)
    if isinstance(item, (tuple, list)):
        return item[int(attribute)]


@register.filter
def cpr(item):
    return f"{item[0:6]}-{item[6:10]}"


@register.filter
def month_name(month_number):
    return util_month_name(month_number)


@register.filter
def after(text, prefix):
    text = str(text)
    try:
        return text[text.index(prefix) + len(prefix) :]
    except ValueError:
        pass
    return text


@register.filter
def after_last(text, prefix):
    text = str(text)
    try:
        return text[text.rindex(prefix) + len(prefix) :]
    except ValueError:
        pass
    return text
