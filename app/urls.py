from django.conf.urls import patterns, url

from app import views

urlpatterns = patterns('',
  url(r'^$', views.index, name='index'),

  # ex: /watch?v=12345678901
  url(r'^watch$', views.watch, name='watch'),

  # ex: /getTaggedComments?v=12345678901
  url(r'^getTaggedComments$', views.getTaggedComments, name='getTaggedComments'),
)
