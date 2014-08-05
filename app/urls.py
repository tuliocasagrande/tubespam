from django.conf.urls import patterns, url

from app import views

urlpatterns = patterns('',
  url(r'^$', views.index, name='index'),
  url(r'^about$', views.about, name='about'),

  # ex: /watch?v=12345678901
  url(r'^watch$', views.watch, name='watch'),

  # ex: /classify?v=12345678901
  url(r'^classify$', views.classify, name='classify'),

  url(r'^saveComment$', views.saveComment, name='saveComment'),
  url(r'^train$', views.train, name='train'),
  url(r'^export$', views.export, name='export'),
  url(r'^reloadClfInfo$', views.reloadClfInfo, name='reloadClfInfo'),
)
