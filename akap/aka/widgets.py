from django.forms import RadioSelect, Select


class TranslatedSelect(Select):
    option_template_name = "widgets/select_option.html"


class TranslatedRadioSelect(RadioSelect):
    option_template_name = "widgets/radio_option.html"
    template_name = "widgets/radio.html"
