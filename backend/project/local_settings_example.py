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

SECRET_KEY = ''


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

OPENID_CONNECT = {
    # top level url to the issuer, used for autodiscovery
    'issuer': 'https://loginqa.sullissivik.gl',
    # openid is mandatory to indicated is is a openid OP, we need to use digitalimik to get the cpr/cvr number.
    'scope': 'openid digitalimik',
    # id of the system (ouath), registered at headnet
    'client_id': 'some company',
    # path to client certificate used to secure the communication between the system and OP
    'client_certificate': '',
    # used for signing messages passed to the OP
    'private_key': '',
    # url registered at headnet to redirect the user to after a successfull login at OP
    'redirect_uri': 'https://akaptest.sullissivik.gl/oid/callback/'
}
