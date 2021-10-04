from django.test import TestCase
import gnupg
import logging
import shutil


class BasicTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.keyname = "TEST KEY"
        cls.folder = '/tmp/gnupg'
        cls.gpg = gnupg.GPG(gnupghome=cls.folder)
        logging.disable(logging.CRITICAL)
        input_data = cls.gpg.gen_key_input(
            key_type="RSA",
            key_length=1024,
            name_real=cls.keyname,
            name_email='me@email.com',
            passphrase='passphrase',
        )
        cls.key = cls.gpg.gen_key(input_data)

    @classmethod
    def tearDownClass(cls):
        try:
            shutil.rmtree(cls.folder)
        finally:
            super().tearDownClass()

    def test_object(self):
        self.assertTrue(isinstance(self.gpg, gnupg.GPG))

    def test_key(self):
        keylist = self.gpg.list_keys(secret=False)  # Only public keys.
        self.assertTrue(len(keylist) > 0)
        keycount = 0
        for key in keylist:
            if key['uids'][0].startswith(self.keyname):
                keycount += 1
        self.assertEqual(keycount, 1)

    def test_encryption(self):
        plaintext = 'Hemmelig tekst her!'
        ciphertext = self.gpg.encrypt(plaintext, self.keyname, always_trust=True)
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
