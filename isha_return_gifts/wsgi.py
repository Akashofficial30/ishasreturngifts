import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'isha_return_gifts.settings')
application = get_wsgi_application()
