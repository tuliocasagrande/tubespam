from django.conf.urls import patterns, url

from app import views

urlpatterns = patterns('',
  url(r'^$', views.index, name='index'),
  url(r'^about$', views.about, name='about'),

  # ex: /watch?v=12345678901
  url(r'^watch$', views.video, name='watch'),
  url(r'^spam$', views.video, name='spam'),
  url(r'^predict$', views.predict, name='predict'),

  url(r'^saveComment$', views.saveComment, name='saveComment'),
  url(r'^export$', views.export, name='export'),
)
