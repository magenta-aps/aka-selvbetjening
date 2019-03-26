from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render


@ensure_csrf_cookie
def IndexView(request):
    # TODO if the user is not logged in redirect the user to a login page
    return render(request, 'index.html', {})
