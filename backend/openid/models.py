from django.db import models
from django.conf import settings


class OpenIdUsers(models.Model):
    # TODO figure out what we can use as PK/ cvr/cpr?
    # and what information do the system/prism needs
    #uuid = models.UUIDField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=False)


#claims
#0	"sub"
#1	"PersonName"
#2	"CVR"
#3	"CPR"
#4	"OrganizationName"
#5	"Email"
#6	"UserType"
#7	"Language"
