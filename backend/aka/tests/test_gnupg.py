from django.test import TestCase, override_settings
from gnupg import GPG
from django.conf import settings
import logging


@override_settings(ENCRYPTED_LOG_KEY_UID='AKA Selvbetjening test')
class BasicTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def test_object(self):
        obj = GPG()
        self.assertTrue(isinstance(obj, GPG))

    def test_key(self):
        gpg = GPG()
        keylist = gpg.list_keys(secret=False)  # Only public keys.
        self.assertTrue(len(keylist) > 0)
        keycount = 0
        for key in keylist:
            if key['uids'][0].startswith(settings.ENCRYPTED_LOG_KEY_UID):
                keycount += 1
        self.assertEqual(keycount, 1)

    def test_encryption(self):
        gpg = GPG()
        plaintext = 'Hemmelig tekst her!'
        ciphertext = gpg.encrypt(plaintext, settings.ENCRYPTED_LOG_KEY_UID, always_trust=True)
        self.assertTrue(ciphertext.ok)

    '''
    We are not decrypting anything in this Django-system,
    but this would be how to do it.
    It requires the private key to be imported to the keyring.
    def test_decryption(self):
        self.importkey(2)
        gpg = GPGWrapper()
        plaintext = 'Hemmelig tekst her!'
        ciphertext = gpg.encrypt(plaintext, self.testfingerprint, True)
        self.assertTrue(ciphertext.ok)
        self.assertTrue(str(ciphertext) != plaintext)
        plaintext2 = gpg.decrypt(str(ciphertext), self.privatekeypwd, True)
        self.assertTrue(plaintext2.ok)
        self.assertEqual(str(plaintext2), plaintext)
    '''
