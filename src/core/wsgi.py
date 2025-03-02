import os
import sys
from django.core.wsgi import get_wsgi_application

sys.path.append("/root/wasooli.online/dev/WasooliBackendServices/src")
sys.path.append("/home/admin/backend/WasooliBackendServices/src")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_wsgi_application()
