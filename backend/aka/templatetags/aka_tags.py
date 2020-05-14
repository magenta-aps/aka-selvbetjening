import json as jsonlib
import re
from html import unescape

from django.template.defaultfilters import register
from django.utils.translation import gettext

trans_re = re.compile("_\\((.*)\\)")
format_re = re.compile("{(.*)}")


@register.filter
def split(text, filter):
    return text.split(filter)


@register.filter
def json(data):
    return jsonlib.dumps(data)


@register.filter
def format(text, params):
    text = gettext(text)
    if params:
        if isinstance(params, str):
            params = jsonlib.loads(params)
        for key in params:
            value = params[key]
            if type(value) == tuple:
                # If a value is a tuple, it must be (message:string, params:dict,)
                value = format(value[0], value[1])
            else:
                value = format(str(value), None)
            text = text.replace("{" + key + "}", value)
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
    return type(text) == str and text.startswith(prefix)


@register.filter
def addstr(arg1, arg2):
    return ''.join([str(a) if a is not None else '' for a in [arg1, arg2]])


@register.filter
def back(url, backurl):
    if backurl:
        return ''.join([
            url,
            '&' if '?' in url else '?',
            'back=',
            urlquote(backurl)
        ])
    return url


@register.filter
def get(item, attribute):
    if hasattr(item, attribute):
        return getattr(item, attribute)
    if hasattr(item, 'get'):
        return item.get(attribute)
