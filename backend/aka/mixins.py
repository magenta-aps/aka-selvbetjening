import json
import os

import pdfkit
from aka.exceptions import AkaException
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.template.loader import get_template
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
            print("form is valid")
            return self.form_valid(form)
        else:
            print("form is not valid")
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


class PdfRendererMixin(object):

    pdf_template_name = ''

    def get_pdf_filename(self):
        raise NotImplementedError

    def render_pdf(self):
        filename = self.get_pdf_filename()
        context = self.get_context_data()

        css_data = []
        for css_file in ['css/output.css', 'css/main.css', 'css/print.css']:
            css_static_path = css_file.split('/')
            css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', *css_static_path)
            if not os.path.exists(css_path):
                css_path = os.path.join(settings.STATIC_ROOT, *css_static_path)
            with open(css_path) as file:
                css_data.append(file.read())
        context['css'] = ''.join(css_data)

        html = get_template(self.pdf_template_name).render(context)
        response = HttpResponse(html)
        # pdf = pdfkit.from_string(html, False)
        # response = HttpResponse(pdf, content_type='application/pdf')
        # response['Content-Disposition'] = "attachment; filename=\"%s\"" % filename
        return response

    def get_context_data(self, **kwargs):
        context = {
            'pdf': 'pdf' in self.request.GET
        }
        context.update(kwargs)
        return super().get_context_data(**context)

