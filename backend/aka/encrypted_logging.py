import logging

from django.conf import settings
from gnupg import GPG


def EncryptedLogFormatterFactory(format=None):
    return EncryptedLogFormatter(format)


class EncryptedLogFormatter(logging.Formatter):

    def __init__(self, format=None, datefmt=None):
        self.gpg = GPG()
        super(EncryptedLogFormatter, self).__init__(fmt=format, datefmt=datefmt)

    def format(self, record):
        s = super(EncryptedLogFormatter, self).format(record)
        return str(self.gpg.encrypt(s, settings.ENCRYPTED_LOG_KEY_UID, always_trust=True))
