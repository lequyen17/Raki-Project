import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'raki.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from payment.views import stripe_topup

user = User.objects.first()
factory = RequestFactory()
request = factory.post('/api/wallet/topup/stripe/', {'amount': 10000, 'redirectUrl': 'http://localhost:3000/app/wallet'}, content_type='application/json')
request.user = user

response = stripe_topup(request)
print("Response status:", response.status_code)
print("Response data:", response.data)
