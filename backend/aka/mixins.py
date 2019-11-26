import json

from aka.exceptions import AkaException
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.views.generic.edit import FormMixin


class ErrorHandlerMixin(object):
    def dispatch(self, request, *args, **kwargs):
        try:
            return super(ErrorHandlerMixin, self).dispatch(request, *args, **kwargs)
        except AkaException as e:
            print({
                'header': e.title,
                'message': e.message,
                'error_code': e.error_code,
                'params': e.params
            })
            return TemplateResponse(
                request=request,
                template="aka/error.html",
                context={
                    'header': e.title,
                    'message': e.message,
                    'error_code': e.error_code,
                    'error_params': json.dumps(e.params)
                },
                using=self.template_engine
            )


class RequireCvrMixin(object):
    def dispatch(self, request, *args, **kwargs):
        # try:
        #     self.cvr = request.session['user_info']['CVR']
        # except (KeyError, TypeError):
        #     raise PermissionDenied('no_cvr')
        self.cvr = '12345678'
        return super(RequireCvrMixin, self).dispatch(request, *args, **kwargs)


class SimpleGetFormMixin(FormMixin):

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        return super().get(self.request)

    def form_invalid(self, form):
        return super().get(self.request)

    def get_form_kwargs(self):
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }
        if self.request.method in ('GET') and len(self.request.GET):
            kwargs.update({
                'data': self.request.GET,
            })
        return kwargs
