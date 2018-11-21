import logging
import json
from django.conf import settings
from gnupg import GPG
import time

def EncryptedLogFormatterFactory():
    return EncryptedLogFormatter()


class EncryptedLogFormatter(logging.Formatter):

    def __init__(self, fmt=None, datefmt=None):
        ''' Init the encryption module.
        '''
        formatstring = '%(asctime)s; %(levelname)s; %(name)s; %(pathname)s; %(lineno)s \n%(message)s'
        self.gpg = GPG()
        super(EncryptedLogFormatter, self).__init__(fmt=formatstring, datefmt=datefmt)

    def format(self, record):
        message = str(record.msg)
        if message:
            message += ' <' + record.pathname + '>' + \
                ' <' + str(record.lineno) + '>' + \
                ' <' + time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(record.created)) + '>'
            record.msg = self.gpg.encrypt(message, settings.PUBLICKEYRECIPIENT, always_trust=True)

        return super(EncryptedLogFormatter, self).format(record)
