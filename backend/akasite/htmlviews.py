from django.views.generic import TemplateView
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render


@ensure_csrf_cookie
def IndexView(request):
    return render(request, 'akasite/index.html', {})
