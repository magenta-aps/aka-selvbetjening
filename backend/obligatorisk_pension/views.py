from django.views.generic import FormView

from project.view_mixins import IsContentMixin
from obligatorisk_pension.forms import ObligatoriskPensionForm


class ObligatoriskPensionView(IsContentMixin, FormView):
    form_class = ObligatoriskPensionForm
    template_name = "pension/form.html"
