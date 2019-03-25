from django.contrib.auth.backends import ModelBackend
from django.conf import settings
from openid.models import OpenIdUsers


class OpenIdAuthenticationBackend(ModelBackend):
    def __init__(self):
        pass

    def authenticate(self, request, username=None, password=None, **kwargs):
        #TODO pass in the claim, setup a user based on that claim if it does not exists, and log the user in

        return None
        pass

    def get_user(self, user_id):
        # TODO:  figure out what to use as the user_id
        """Return a user based on the id."""
        try:
            return self.UserModel.objects.get(pk=user_id)
        except self.UserModel.DoesNotExist:
            return None