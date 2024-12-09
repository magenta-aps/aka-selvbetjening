# SPDX-FileCopyrightText: 2023 Magenta ApS <info@magenta.dk>
#
# SPDX-License-Identifier: MPL-2.0

from datetime import date
from typing import Optional

from django.shortcuts import get_object_or_404
from ninja import Field, FilterSchema, ModelSchema, NinjaAPI, Query
from ninja.security import HttpBearer
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema
from project.settings.api import API_GLOBAL_SECRET
from udbytte.models import U1A, U1AItem


class GlobalStaticAuth(HttpBearer):
    def authenticate(self, request, token):
        if token == API_GLOBAL_SECRET:
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
    class Meta:
        model = U1AItem
        fields = "__all__"


class U1AItemFilterSchema(FilterSchema):
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
def get_u1a_entries(request, filters: U1AFilterSchema = Query(...)):
    return filters.filter(U1A.objects.all())


@api.get(
    "/u1a/{u1a_id}/items",
    response=NinjaPaginationResponseSchema[U1AItemOut],
    url_name="u1a_item_list",
)
@paginate()
def get_u1a_item_entries(
    request, u1a_id: int, filters: U1AItemFilterSchema = Query(...)
):
    u1a = get_object_or_404(U1A, pk=u1a_id)
    return U1AItem.objects.filter(u1a_id=u1a.id)
