from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
  url(r'^admin/', include(admin.site.urls)),
  url(r'^$', 'app.views.index', name='index'),

  # ex: /watch?v=12345678901
  url(r'^watch$', 'app.views.watch', name='watch'),
)
