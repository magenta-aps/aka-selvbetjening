import logging
from django.conf import settings
from gnupg import GPG
import time


def EncryptedLogFormatterFactory():
    return EncryptedLogFormatter()

# NOTE TO SELF: registrér 3 timer på #25312 d. 08.10.2020

class EncryptedLogFormatter(logging.Formatter):

    def __init__(self, fmt=None, datefmt=None):
        formatstring = '%(asctime)s %(levelname)s %(name)s %(pathname)s:%(lineno)s    %(message)s'
        self.gpg = GPG()
        super(EncryptedLogFormatter, self).__init__(fmt=formatstring, datefmt=datefmt)

    def format(self, record):
        s = super(EncryptedLogFormatter, self).format(record)
        return str(self.gpg.encrypt(s, settings.ENCRYPTED_LOG_KEY_UID, always_trust=True))
