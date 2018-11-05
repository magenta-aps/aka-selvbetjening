import random
generated_secret_key = ''.join([
         random.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
         for i in range(50)
     ])

print(
        """
# Use this file to override settings from the settings.py file

# Set up a local secret_key to protect user passwords and sessions
# Can be generated with:
# python -c "import random; print(
# ''.join([
#     random.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
#     for i in range(50)
# ])
# )"

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
""" + "\nSECRET_KEY = '{0}'".format(generated_secret_key) +
"""

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
    """
    )
