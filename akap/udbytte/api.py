# SPDX-FileCopyrightText: 2023 Magenta ApS <info@magenta.dk>
#
# SPDX-License-Identifier: MPL-2.0

from datetime import date
from typing import Optional

from django.conf import settings
from ninja import Field, FilterSchema, ModelSchema, NinjaAPI, Query
from ninja.security import HttpBearer
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema
from udbytte.models import U1A, U1AItem


class GlobalStaticAuth(HttpBearer):
    def authenticate(self, request, token):
        if token == settings.API_GLOBAL_SECRET:
            return token


api = NinjaAPI(auth=GlobalStaticAuth())


class U1AOut(ModelSchema):
    class Meta:
        model = U1A
        fields = "__all__"


class U1AFilterSchema(FilterSchema):
    navn: Optional[str] = None
    revisionsfirma: Optional[str] = None
    virksomhedsnavn: Optional[str] = None
    cvr: Optional[str] = None
    email: Optional[str] = None
    regnskabsår: Optional[int] = None
    u1_udfyldt: Optional[str] = None
    noter: Optional[str] = None
    by: Optional[str] = None
    dato: Optional[str] = None
    underskriftsberettiget: Optional[str] = None
    oprettet_efter: Optional[date] = Field(
        default=None, json_schema_extra={"q": "oprettet__gte"}
    )
    oprettet_før: Optional[date] = Field(
        default=None, json_schema_extra={"q": "oprettet__lt"}
    )
    oprettet_af_cpr: Optional[str] = None
    oprettet_af_cvr: Optional[str] = None


class U1AItemOut(ModelSchema):
    u1a: U1AOut  # Explicitly declare this as nested schema

    class Meta:
        model = U1AItem
        fields = "__all__"
        exclude = ["u1a"]


class U1AItemFilterSchema(FilterSchema):
    u1a: Optional[str] = None
    cpr_cvr_tin: Optional[str] = None
    navn: Optional[str] = None
    adresse: Optional[str] = None
    postnummer: Optional[str] = None
    by: Optional[str] = None
    land: Optional[str] = None
    oprettet_efter: Optional[date] = Field(
        default=None, json_schema_extra={"q": "oprettet__gte"}
    )
    oprettet_før: Optional[date] = Field(
        default=None, json_schema_extra={"q": "oprettet__lt"}
    )


@api.get(
    "/u1a",
    response=NinjaPaginationResponseSchema[U1AOut],
    url_name="u1a_list",
)
@paginate()
def get_u1a_entries(
    request,
    filters: U1AFilterSchema = Query(...),
    year: Optional[int] = None,
    cpr: Optional[str] = None,
):
    print(f"year: {year}")
    print(f"cpr: {cpr}")
    qs = filters.filter(U1A.objects.all())
    if year:
        qs = qs.filter(dato_vedtagelse__year=year)

    if cpr:
        qs = qs.filter(u1aitem__cpr_cvr_tin=cpr).distinct()

    return qs


@api.get(
    "/u1a-items",
    response=NinjaPaginationResponseSchema[U1AItemOut],
    url_name="u1a_item_list",
)
@paginate()
def get_u1a_item_entries(
    request, filters: U1AItemFilterSchema = Query(...), year: Optional[int] = None
):
    qs = filters.filter(U1AItem.objects.all().select_related("u1a"))
    if year:
        qs = qs.filter(u1a__dato_vedtagelse__year=year)

    return qs


@api.get(
    "/u1a-items/unique/cprs",
    response=NinjaPaginationResponseSchema[str],
    url_name="u1a_item_unique_cprs",
)
@paginate()
def get_u1a_items_unique_cprs(
    request, filters: U1AItemFilterSchema = Query(...), year: Optional[int] = None
):
    qs = filters.filter(U1AItem.objects.all())

    if year:
        qs = qs.filter(u1a__dato_vedtagelse__year=year)

    return qs.values_list("cpr_cvr_tin", flat=True).distinct()
