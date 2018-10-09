from django.views.generic import TemplateView
from django.views import View


class IndexView(TemplateView):
    template_name = 'akasite/index.html'


class Indberetning(TemplateView):
    template_name = 'akasite/indberet_fordring.html'


