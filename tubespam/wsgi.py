"""
WSGI config for tubespam project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import newrelic.agent
import os
from django.core.wsgi import get_wsgi_application

os.environ["DJANGO_SETTINGS_MODULE"] = "tubespam.settings"

def application(environ, start_response):
  for key in environ:
    if key.startswith('TS_'):
      os.environ[key] = environ[key]

  newrelic.agent.initialize(os.environ['TS_NEW_RELIC_CONFIG_FILE'],
                            os.environ['TS_NEW_RELIC_ENVIRONMENT'])
  return get_wsgi_application()(environ, start_response)
