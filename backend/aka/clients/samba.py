import re
import tempfile
from abc import ABCMeta, abstractmethod

import smbc
import stat

from django.conf import settings
from smb.SMBConnection import SMBConnection


class SambaException(Exception):
    pass


class SambaEntry(object):
    def __init__(self, is_directory, name, filesize):
        self.is_directory = is_directory
        self.name = name
        self.filesize = filesize


class SambaClient(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def list_dir(self, path):
        raise NotImplementedError

    @abstractmethod
    def get_entry(self, path):
        raise NotImplementedError

    @abstractmethod
    def get_contents(self, path):
        raise NotImplementedError

    @staticmethod
    def _normalize_path(path):
        return re.sub('//+', '/', path)


class PySmbClient(SambaClient):

    host = settings.MOUNTS
    client_name = 'AKA Selvbetjening'

    def __init__(self, configname):
        config = settings.MOUNTS[configname]
        self.host = config['host']
        self.share = config['share']
        self.username = config['username']
        self.password = config['password']
        self._connection = None

    @property
    def client(self):
        if not self._connection:
            self._connection = SMBConnection(self.username, self.password, self.client_name, self.host)
            connected = self._connection.connect(self.host, 139)
            if not connected:
                raise SambaException("Could not connect to server")
        return self._connection

    def list_dir(self, path):
        return [
            self._entry(entry)
            for entry in self.client.listPath(self.share, path)
            if entry.filename not in ['.','..']
        ]

    def get_entry(self, path):
        return self._entry(self.client.getAttributes(self.share, path))

    def _entry(self, sharedfile):
        return SambaEntry(sharedfile.isDirectory, sharedfile.filename, sharedfile.file_size)

    def get_contents(self, path):
        # file = open('/tmp/test', 'wb+')
        # with file:
        #     self.client.retrieveFile(self.share, path, file)
        # file = open('/tmp/test', 'rb+')
        # return file
        file = tempfile.NamedTemporaryFile('w+b')
        self.client.retrieveFile(self.share, path, file)
        self.client.close()
        return file


class SmbcClient(SambaClient):

    host = settings.MOUNTS
    client_name = 'AKA Selvbetjening'

    def __init__(self, configname):
        config = settings.MOUNTS[configname]
        self.host = config['host']
        self.share = config['share']
        self.username = config['username']
        self.password = config['password']
        self._connection = None

    @property
    def client(self):
        if not self._connection:
            self._connection = smbc.Context(auth_fn=lambda se, sh, w, u, p: (w, self.username, self.password))
        return self._connection

    def list_dir(self, path):
        path = self._normalize_path(path)
        dirents = self.client.opendir('smb://' + self.host + '/' + self.share + path).getdents()
        return [
            self.get_entry(path + '/' + entry.name)
            for entry in dirents
            if entry.name not in ['.', '..']
        ]

    def get_entry(self, path):
        path = self._normalize_path(path)
        st = self.client.stat('smb://' + self.host + '/' + self.share + path)
        return SambaEntry(stat.S_ISDIR(st[stat.ST_MODE]), path.split('/')[-1], st[stat.ST_SIZE])

    def get_contents(self, path):
        file = self._connection.open('smb://' + self.host + '/' + self.share + path)
        return file
