from django.contrib.auth.models import AnonymousUser

# Create your models here.
from django.utils.deprecation import CallableTrue


class SessionOnlyUserPkField(object):
    def value_to_string(self):
        return 'foo'


class SessionOnlyUser(AnonymousUser):

    cpr = None
    name = None

    def __str__(self):
        return 'SessionOnlyUser'

    def __init__(self, cpr, name):
        super(SessionOnlyUser, self).__init__()
        self.cpr = cpr
        self.name = name

    @property
    def is_authenticated(self):
        return CallableTrue

    def dict(self):
        return {'cpr': self.cpr, 'name': self.name}

    @staticmethod
    def get_user(session, cpr=None, name=None):
        user_dict = session.get('user')
        if cpr is not None:
            user_dict = {'cpr': cpr, 'name': name}
            session['user'] = user_dict
        elif user_dict is None:
            return AnonymousUser()
        return SessionOnlyUser(
            user_dict.get('cpr'), user_dict.get('name', name)
        )
