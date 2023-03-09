from django.forms import Select
from django.forms import RadioSelect


class TranslatedSelect(Select):
    option_template_name = "widgets/select_option.html"


class TranslatedRadioSelect(RadioSelect):
    option_template_name = "widgets/radio_option.html"
