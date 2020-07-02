from django.urls import path, re_path
from . import views

urlpatterns = [
    path('get_token/', views.get_token, name='get_token'),
    path('set_link/', views.set_link, name='set_link'),
    path('analytic/', views.get_analytic, name='get_analytic'),
    path('top_analytic/', views.get_top_analytic, name='get_top_analytic'),
    re_path('^(?P<short_url>.{6})/$', views.redirect_link, name='visit_link'),
]
