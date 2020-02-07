"""akaURL Configuration

The`urlpatterns` list routes URLs to views. For more information please see:
   https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Functionviews
   1. Add an import:  from my_app import views
   2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-basedviews
   1. Add an import:  from other_app.views import Home
   2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Includinganother URLconf
   1. Import the include() function: from django.conf.urls import url, include
   2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from aka.views import ArbejdsgiverKontoView
from aka.views import BorgerKontoView
from aka.views import CustomJavaScriptCatalog, SetLanguageView
from aka.views import FordringshaverkontoView
from aka.views import IndexTemplateView
from aka.views import InkassoGroupDataView
from aka.views import InkassoSagView, InkassoSagUploadView
from aka.views import LoenTraekDistributionView
from aka.views import LoentraekView, LoentraekUploadView
from aka.views import LoginView, LogoutView
from aka.views import NedskrivningView, NedskrivningUploadView
from aka.views import NetsopkraevningView
from aka.views import RenteNotaView
from django.conf.urls import url

app_name = 'aka'

urlpatterns = [
    # Use 'django' domain instead of 'djangojs', so we get serverside translations
    url(r'^language/(?P<locale>[a-z]{2})', CustomJavaScriptCatalog.as_view(domain='django', packages=['aka']), name='javascript-language-catalog'),
    url(r'^language', SetLanguageView.as_view(), name='set-language'),

    url(r'^$', IndexTemplateView.as_view(), name='index'),
    url(r'^login$', LoginView.as_view(), name='login'),
    url(r'^logout$', LogoutView.as_view(), name='logout'),
    url(r'^inkassosag$', InkassoSagView.as_view(), name='inkassosag'),
    url(r'^inkassosag/upload', InkassoSagUploadView.as_view(), name='inkassosag-upload'),
    url(r'^fordringsgrupper/(?P<var>[a-z_]+)?', InkassoGroupDataView.as_view(), name='fordringsgrupper'),
    url(r'^loentraek$', LoentraekView.as_view(), name='loentraek'),
    url(r'^loentraek/upload', LoentraekUploadView.as_view(), name='loentraek-upload'),
    url(r'^loentraekdistribution/([0-9]{8})$', LoenTraekDistributionView.as_view(), name='loentraekdistribution'),
    url(r'^rentenota/$', RenteNotaView.as_view(), name='rentenota'),
    url(r'^nedskrivning$', NedskrivningView.as_view(), name='nedskrivning'),
    url(r'^nedskrivning/upload$', NedskrivningUploadView.as_view(), name='nedskrivning-upload'),
    url(r'^netsopkraevning$', NetsopkraevningView.as_view(), name='netsopkraevning'),
    url(r'^fordringshaverkonto(?P<path>/.*)$', FordringshaverkontoView.as_view(), name='fordringshaverkonto-path'),
    url(r'^fordringshaverkonto/$', FordringshaverkontoView.as_view(), name='fordringshaverkonto', kwargs={'path': '/'}),
    url(r'^arbejdsgiverkonto$', ArbejdsgiverKontoView.as_view(), name='arbejdsgiverkonto'),
    url(r'^borgerkonto$', BorgerKontoView.as_view(), name='borgerkonto'),
]
