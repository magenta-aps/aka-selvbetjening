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
from django.conf.urls import url, include

from .views import ArbejdsgiverkontoView
from .views import FordringshaverkontoView
from .views import IndexTemplateView
from .views import InkassoSagView
from .views import LoenTraekDistributionView
from .views import LoenTraekView
from .views import NedskrivningView
from .views import NetsopkraevningView
from .views import PrivatdebitorkontoView
from .views import RenteNotaView

urlpatterns = [
   url(r'^$', IndexTemplateView.as_view(), name='index'),

   url(r'^oid/', include('openid.urls', namespace='openid')),

   url(r'^inkassosag$',
       InkassoSagView.as_view(),
       name='inkassosag'),

   url(r'^loentraek$',
       LoenTraekView.as_view(),
       name='loentraek'),

   url(r'^loentraekdistribution/([0-9]{8})$',
       LoenTraekDistributionView.as_view(),
       name='loentraekdistribution'),

   url(r'^rentenota/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})$',
       RenteNotaView.as_view(),
       name='rentenota'),

   url(r'^nedskrivning$',
       NedskrivningView.as_view(),
       name='nedskrivning'),

   url(r'^netsopkraevning$',
       NetsopkraevningView.as_view(),
       name='netsopkraevning'),

   url(r'^fordringshaverkonto$',
       FordringshaverkontoView.as_view(),
       name='fordringshaverkonto'),

   url(r'^arbejdsgiverkonto$',
       ArbejdsgiverkontoView.as_view(),
       name='arbejdsgiverkonto'),

   url(r'^privatdebitorkonto$',
       PrivatdebitorkontoView.as_view(),
       name='privatdebitorkonto'),
]
