import posixpath
from django.conf import settings
from django.db import models
from django.utils.datetime_safe import datetime
from django.utils.translation import gettext_lazy as _


class ObligatoriskPension(models.Model):
    oprettet = models.DateTimeField(
        auto_now_add=True,
    )
    ændret = models.DateTimeField(
        auto_now=True,
    )
    cpr = models.CharField(
        max_length=10,
        null=False,
        blank=False,
    )
    skatteår = models.PositiveSmallIntegerField(
        null=False,
        blank=False,
    )
    navn = models.CharField(
        null=False,
        blank=False,
        max_length=1000,
    )
    adresse = models.CharField(
        null=False,
        blank=False,
        max_length=1000,
    )
    kommune = models.PositiveSmallIntegerField(
        choices=((m["code"], m["name"]) for m in settings.MUNICIPALITIES),
        null=False,
    )
    email = models.EmailField(
        null=False,
        blank=False,
        max_length=256,
    )


class ObligatoriskPensionSelskab(models.Model):
    grønlandsk = models.BooleanField(
        choices=(
            (True, _("Ja")),
            (False, _("Nej")),
        ),
        null=False,
        blank=False,
    )
    land = models.CharField(
        null=True,
        blank=True,
        max_length=50,
    )
    pensionsselskab = models.CharField(
        null=False,
        blank=False,
        max_length=100,
    )
    obligatoriskpension = models.ForeignKey(
        ObligatoriskPension,
        on_delete=models.CASCADE,
        related_name="selskaber",
    )


def obligatoriskpensionfile_upload_to(instance, filename):
    dirname = (
        datetime.now().strftime("obligatorisk_pension/%Y/%Y-%m-%d/")
        + instance.obligatoriskpension.cpr
    )
    filename = posixpath.join(dirname, filename)
    return filename


class ObligatoriskPensionFile(models.Model):
    fil = models.FileField(upload_to=obligatoriskpensionfile_upload_to)
    beskrivelse = models.CharField(max_length=1000, null=True, blank=True)
    obligatoriskpension = models.ForeignKey(
        ObligatoriskPension,
        on_delete=models.CASCADE,
        related_name="filer",
    )
