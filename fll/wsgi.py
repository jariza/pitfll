"""
WSGI config for fll project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

#Requerido por AWS lightsail
import sys
sys.path.append('/home/bitnami/stack/projects/flldj')
os.environ.setdefault("PYTHON_EGG_CACHE", "/home/bitnami/stack/projects/flldj/egg_cache")
#Fin de Requerido por AWS lightsail

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fll.settings')

application = get_wsgi_application()
