# SPDX-FileCopyrightText: 2023 Magenta ApS <info@magenta.dk>
#
# SPDX-License-Identifier: MPL-2.0

from datetime import date

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class U1A(models.Model):
    # Field helpers
    @staticmethod
    def get_financial_year_choices():
        current_year = date.today().year
        return [(year, str(year)) for year in range(current_year, current_year - 6, -1)]

    # Fields
    navn = models.CharField(
        verbose_name=_("Navn på udfylder"),
        max_length=255,
        error_messages={"required": "error.required"},
    )

    revisionsfirma = models.CharField(verbose_name=_("Revisionsfirma"), max_length=255)

    virksomhedsnavn = models.CharField(
        verbose_name=_("Virksomhedsnavn"),
        max_length=255,
        error_messages={"required": "error.required"},
    )

    cvr = models.CharField(
        verbose_name=_("CVR"),
        max_length=255,
        error_messages={"required": "error.required", "invalid": "error.invalid_cvr"},
    )

    email = models.CharField(
        verbose_name=_("Email-adresse"),
        max_length=255,
        error_messages={"required": "error.required", "invalid": "error.invalid_email"},
    )

    regnskabsår = models.IntegerField(
        verbose_name=_("Udbyttet vedrører regnskabsåret"),
        choices=get_financial_year_choices(),
    )

    u1_udfyldt = models.BooleanField(
        verbose_name=_("Har du allerede udfyldt U1?"),
        choices=[
            (None, "---------"),
            ("0", "No"),
            ("1", "Yes"),
        ],
        blank=True,
        null=True,
    )

    udbytte = models.DecimalField(
        verbose_name=_("Udbetalt/godskrevet udbytte i DKK, før skat"),
        max_digits=12,
        decimal_places=2,  # For currency, typically two decimal places
        error_messages={
            "required": "error.required",
            "invalid": "error.number_required",
        },
    )

    noter = models.TextField(
        verbose_name=_("Særlige oplysninger"),
        blank=True,
        null=True,
    )

    by = models.CharField(
        verbose_name=_("By"),
        max_length=255,
        error_messages={
            "required": "error.required",
        },
    )

    dato = models.DateField(
        verbose_name=_("Dato"),
        error_messages={
            "required": "error.required",
            "invalid": "error.invalid_date",
        },
    )

    underskriftsberettiget = models.CharField(
        verbose_name=_("Navn på underskriftsberettiget for selskabet"),
        max_length=255,  # Adjust based on the maximum expected length for a name
        error_messages={
            "required": "error.required",
        },
    )

    oprettet = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    oprettet_af_cpr = models.CharField(
        db_index=True,
        verbose_name=_("Oprettet af CPR"),
        error_messages={"required": "error.required"},
    )

    oprettet_af_cvr = models.CharField(
        db_index=True,
        verbose_name=_("Oprettet af CVR"),
        blank=True,
        null=True,
    )


class U1AItem(models.Model):
    u1a = models.ForeignKey(
        U1A,
        on_delete=models.CASCADE,
    )

    cpr_cvr_tin = models.CharField(
        verbose_name=_("CPR-nr / CVR-nr / TIN"),
        validators=[RegexValidator(r"^\d{8}(\d{2})?$", "error.invalid_cpr_cvr")],
        error_messages={
            "required": "error.required",
            "invalid": "error.invalid_cpr_cvr",
        },
    )

    navn = models.CharField(
        verbose_name=_("Navn"),
        error_messages={"required": "error.required"},
    )

    adresse = models.CharField(
        verbose_name=_("Adresse"),
        error_messages={"required": "error.required"},
    )

    postnummer = models.CharField(
        verbose_name=_("Postnummer"),
        error_messages={"required": "error.required"},
    )

    by = models.CharField(
        verbose_name=_("By"),
        error_messages={"required": "error.required"},
    )

    land = models.CharField(
        verbose_name=_("Land"),
        error_messages={"required": "error.required"},
    )

    udbytte = models.DecimalField(
        verbose_name=_("Udbetalt/godskrevet udbytte i DKK, før skat"),
        max_digits=12,
        decimal_places=2,
        error_messages={
            "required": "error.required",
            "invalid": "error.number_required",
        },
    )

    oprettet = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )
