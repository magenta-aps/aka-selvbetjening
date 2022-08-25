from django.urls import path
from django.conf import settings

app_name = 'mitid_test'

urlpatterns = []

if settings.LOGIN_PROVIDER_CLASS in ('django_mitid_auth.saml.saml2.Saml2', 'django_mitid_auth.saml.oiosaml.OIOSaml'):
    from mitid_test import views

    urlpatterns += [
        path('clear_session/', views.ClearSessionView.as_view()),
        path('privilege0/', views.Privilege0View.as_view()),
        path('privilege1/', views.Privilege1View.as_view()),
        path('privilege3/', views.Privilege3View.as_view()),
        path('force_auth/', views.ForceAuthView.as_view()),
        path('show_session/', views.ShowSession.as_view()),
        path('list_sessions/', views.ListSessions.as_view()),
    ]
