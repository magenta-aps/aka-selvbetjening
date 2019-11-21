from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
import json

from aka.exceptions import AkaException, AccessDeniedException


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
        try:
            # self.cvr = request.session['user_info']['CVR']
            self.cvr = '12345678'
        except (KeyError, TypeError):
            raise PermissionDenied('no_cvr')
        return super(RequireCvrMixin, self).dispatch(request, *args, **kwargs)
