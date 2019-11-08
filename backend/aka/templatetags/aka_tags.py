import json as jsonlib
from html import unescape

from django.template.defaultfilters import register

@register.filter
def split(text, filter):
    return text.split(filter)

@register.filter
def json(data):
    return jsonlib.dumps(data)


@register.filter
def format(text, params):
    if params:
        for key in params:
            text = text.replace("{" + key + "}", str(params[key]))
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
