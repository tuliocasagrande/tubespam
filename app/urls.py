from django.conf.urls import patterns, url

from app import views

urlpatterns = patterns('',
  url(r'^$', views.index, name='index'),
  url(r'^about$', views.about, name='about'),

  # ex: /watch?v=12345678901
  url(r'^watch$', views.watch, name='watch'),

  # ex: /getTaggedComments?v=12345678901
  url(r'^getTaggedComments$', views.getTaggedComments, name='getTaggedComments'),

  url(r'^saveComment$', views.saveComment, name='saveComment'),

  # ex: /classify?v=12345678901
  url(r'^classify$', views.classify, name='classify'),
)
