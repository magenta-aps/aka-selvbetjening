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
from django.contrib import admin
from django.views.generic.base import RedirectView

from aka import htmlviews
from aka.rest import inkassosag, \
                    loentraek, \
                    loentraekdistribution, \
                    rentenota, \
                    nedskrivning, \
                    netsopkraevning, \
                    fordringshaverkonto, \
                    arbejdsgiverkonto, \
                    privatdebitorkonto



urlpatterns = [

   url(r'^admin/',
       admin.site.urls),
   # redirect empty url string to index

   url(r'^$',
       RedirectView.as_view(url='/index', permanent=False),
       name='index'),

   url(r'^index$',
       htmlviews.IndexView,
       name='index'),

   url(r'^oid/', 
       include('openid.urls', namespace='openid')),
  
   url(r'^inkassosag$',
       inkassosag.InkassoSag.as_view(),
       name='inkassosag'),

   url(r'^loentraek$',
       loentraek.LoenTraek.as_view(),
       name='loentraek'),

   url(r'^loentraekdistribution/([0-9]{8})$',
       loentraekdistribution.LoenTraekDistribution.as_view(),
       name='loentraekdistribution'),

   url(r'^rentenota/(?P<cvr>[0-9]{8})/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})$',
       rentenota.RenteNota.as_view(),
       name='rentenota'),

   url(r'^nedskrivning$',
       nedskrivning.Nedskrivning.as_view(),
       name='nedskrivning'),

   url(r'^netsopkraevning$',
       netsopkraevning.Netsopkraevning.as_view(),
       name='netsopkraevning'),

   url(r'^fordringshaverkonto$',
       fordringshaverkonto.Fordringshaverkonto.as_view(),
       name='fordringshaverkonto'),

   url(r'^arbejdsgiverkonto$',
       arbejdsgiverkonto.Arbejdsgiverkonto.as_view(),
       name='arbejdsgiverkonto'),

   url(r'^privatdebitorkonto$',
       privatdebitorkonto.Privatdebitorkonto.as_view(),
       name='privatdebitorkonto'),
]
