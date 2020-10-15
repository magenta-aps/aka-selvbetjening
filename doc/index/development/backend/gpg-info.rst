Encryption
==========

Using GPG
---------

In order to use GnuPG with Python, install gnupg (apt-get?), and
python-gnupg (pip install python-gnupg==0.4.3).
I have been looking at this one:

https://gnupg.readthedocs.io/en/latest/#

Create the test key pair on a separate computer, not a VM.
The public key should be imported as part of server setup,
as the unit tests expects it to be present.

On a virtual machine, it takes a few seconds to create a key pair with length 1024,
but with key length set to 2048, it is extremely slow.
Also, if you do use gpg to create a key pair on the target server, you will also get 
the private key in the keyring, which is not wanted.
So, create the key pair on a separate computer, and import the public key to the target server.

GPG commands
------------

- Create key pair interactively:

    .. code-block:: text

        gpg --gen-key

- Create key pair for testing via argument file:

    .. code-block:: text

        Key-Type: RSA

        Subkey-Type: default

        Key-Length: 4096

        Name-Real: pythontestkey

        Name-Comment: Test key for use with unit testing.

        Name-Email: ikkenogen@magenta.dk

        Passphrase: testpwd

        %commit

        %echo done

- Create the key pair. NB: This imports both public and private keys into your keyring, so do not do this on the server.

    .. code-block:: text

        cat argsfile.txt | gpg --gen-key --batch

- Export the public key in ASCII form:

    .. code-block:: text

        gpg --output pythontestkey.pub --armor --export pythontestkey

- Import the public key from an exported file:

    .. code-block:: text

     gpg --import pythontestkey.pub

- List private keys:

    .. code-block:: text

        gpg -K

- List public keys:

    .. code-block:: text

        gpg -k

- Encrypt with public key for 'pythontestkey':

    .. code-block:: text

        gpg --output encrypted.gpg --recipient pythontestkey --encrypt plain.txt

- Decrypt file:

    .. code-block:: text

        gpg --output plain2.txt --decrypt encrypted.gpg

- Export the private key in ASCII form:

    .. code-block:: text

        gpg --output pythontestkey.priv --armor --export-secret-keys pythontestkey

- Delete a key pair:

    .. code-block:: text

        gpg --delete-secret-and-public-key <fingerprint|ID>

Using Postgresql
----------------

Create a table for the data:

    .. code-block:: sql

        create table privattabel(id serial primary key,
            username varchar(50),
            privatedata bytea);

Create a table for the key:

    .. code-block:: sql

        create table publickeys(id serial primary key,
            keyname varchar(200),
            fingerprint varchar(200),
            pubkey varchar);

Create the key pair with gpg, export the public key in ASCII form, and insert
it into table publickeys.
Insert encrypted text:


    .. code-block:: sql

        insert into privattabel (username, privat)
            values ('michael',
            pgp_pub_encrypt('Secret text here.',
                (select dearmor(pubkey) from publickeys where keyname =
                'postgresqltestkey')
                )
           );

Decrypt the stored text:

    .. code-block:: sql

        select pgp_pub_decrypt(privat,
            (select dearmor(privatekey) from publickeys where keyname = 'postgresqltestkey'),
            'testpwd')
            from privattabel;
