import logging
from django.conf import settings
from gnupg import GPG
import time


def EncryptedLogFormatterFactory(format=None):
    return EncryptedLogFormatter(format)

# NOTE TO SELF: registrér 3 timer på #25312 d. 08.10.2020

class EncryptedLogFormatter(logging.Formatter):

    def __init__(self, format=None, datefmt=None):
        # formatstring = '%(asctime)s %(levelname)s %(name)s %(pathname)s:%(lineno)s    %(message)s'
        self.gpg = GPG()
        super(EncryptedLogFormatter, self).__init__(fmt=format, datefmt=datefmt)

    def format(self, record):
        s = super(EncryptedLogFormatter, self).format(record)
        return str(self.gpg.encrypt(s, settings.ENCRYPTED_LOG_KEY_UID, always_trust=True))
