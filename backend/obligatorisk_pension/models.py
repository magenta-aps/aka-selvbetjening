from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class ObligatoriskPension(models.Model):
    cpr = models.CharField(
        max_length=10,
        null=False,
        blank=False,
    )
    navn = models.CharField(
        verbose_name=_("obligatorisk_pension.navn"),
        null=False,
        blank=False,
        max_length=1000,
    )
    adresse = models.CharField(
        verbose_name=_("obligatorisk_pension.adresse"),
        null=False,
        blank=False,
        max_length=1000,
    )
    kommune = models.PositiveSmallIntegerField(
        choices=((m["code"], m["name"]) for m in settings.MUNICIPALITIES),
        null=False,
    )
    email = models.EmailField(
        verbose_name=_("obligatorisk_pension.email"),
        null=False,
        blank=False,
        max_length=256,
    )
    grønlandsk = models.BooleanField(
        verbose_name=_("obligatorisk_pension.grønlandsk"),
        choices=(
            (True, _("Ja")),
            (False, _("Nej")),
        ),
        null=False,
        blank=False,
    )
    land = models.CharField(
        verbose_name=_("obligatorisk_pension.land"),
        null=True,
        blank=True,
        max_length=50,
    )
    pensionsselskab = models.CharField(
        verbose_name=_("obligatorisk_pension.pensionsselskab"),
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
