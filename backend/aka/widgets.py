from django.forms import Select

class TranslatedSelect(Select):
    option_template_name = 'widgets/select_option.html'
