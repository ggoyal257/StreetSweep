from django.conf.urls import patterns, url

from sweep import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    #url(r'^(?P<latitude>\f+)/(?P<longitude>\f+)/', views.getWard, name='getWard'),
    url(r'^(-?\d+\.\d+)/(-?\d+\.\d+)/', views.getWard, name='getWard'),
)