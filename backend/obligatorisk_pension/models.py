from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class ObligatoriskPension(models.Model):
    navn = models.CharField(
        verbose_name=_("Navn"),
        null=False,
        blank=False,
        max_length=1000,
    )
    adresse = models.CharField(
        verbose_name=_("Adresse"),
        null=False,
        blank=False,
        max_length=1000,
    )
    kommune = models.PositiveSmallIntegerField(
        choices=((m["code"], m["name"]) for m in settings.MUNICIPALITIES),
        null=False,
    )
    email = models.EmailField(
        verbose_name=_("Email-adresse"),
        null=False,
        blank=False,
        max_length=256,
    )
    grønlandsk = models.BooleanField(
        verbose_name=_("Grønlandsk pensionsordning"),
        choices=(
            (True, _("Ja")),
            (False, _("Nej")),
        ),
        null=False,
        blank=False,
    )
    land = models.CharField(
        verbose_name=_("Land"),
        null=True,
        blank=True,
        max_length=50,
    )
    pensionsselskab = models.CharField(
        verbose_name=_("Pensionsselskab"),
        null=False,
        blank=False,
        max_length=100,
    )


class ObligatoriskPensionFile(models.Model):
    fil = models.FileField(upload_to="obligatorisk_pension/%Y/%Y-%m-%d/")
    beskrivelse = models.CharField(
        max_length=1000,
    )
    obligatoriskpension = models.ForeignKey(
        ObligatoriskPension,
        on_delete=models.CASCADE,
        related_name="files",
    )
