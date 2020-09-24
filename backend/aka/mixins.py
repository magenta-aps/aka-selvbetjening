import json
import os

import django_excel as excel
import pdfkit
from aka.clients.dafo import Dafo
from aka.clients.prisme import Prisme
from aka.clients.prisme import PrismeCvrCheckRequest
from aka.clients.prisme import PrismeNotFoundException
from aka.exceptions import AkaException
from aka.utils import flatten
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template.loader import select_template
from django.template.response import TemplateResponse
from django.urls import reverse
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
                template="aka/util/error.html",
                context={
                    'header': e.title,
                    'message': e.message,
                    'error_code': e.error_code,
                    'error_params': json.dumps(e.params)
                },
                using=self.template_engine
            )


class HasUserMixin(object):

    def __init__(self, *args, **kwargs):
        self.cvr = None
        self.cpr = None
        self.claimant_ids = []
        self.company = None
        self.person = None
        super().__init__(*args, **kwargs)

    def get_claimants(self, request):
        if 'claimantIds' in request.session:
            return request.session['claimantIds']
        elif self.cvr is not None:
            try:
                cvr = self.cvr
                claimant_ids = flatten([
                    response.claimant_id
                    for response in Prisme().process_service(PrismeCvrCheckRequest(cvr), 'cvr_check')
                ])
                request.session['claimantIds'] = claimant_ids
                request.session.save()
                return claimant_ids
            except PrismeNotFoundException as e:
                return []

    def get_company(self, request):
        if 'company' in request.session['user_info']:
            return request.session['user_info']['company']
        elif self.cvr is not None:
            company = Dafo().lookup_cvr(self.cvr)
            request.session['user_info']['company'] = company
            return company

    def get_person(self, request):
        if 'person' in request.session['user_info']:
            return request.session['user_info']['person']
        elif self.cpr is not None:
            person = Dafo().lookup_cpr(self.cpr, False)
            request.session['user_info']['person'] = person
            return person

    def dispatch(self, request, *args, **kwargs):
        try:
            self.cpr = request.session['user_info']['CPR']
            self.person = {'navn': request.session['user_info']['name']}
            self.p = self.get_person(request)
        except (KeyError, TypeError):
            pass

        if self.cpr and not self.cvr and not request.session.get('has_checked_cvr'):
            cvrs = Dafo().lookup_cvr_by_cpr(self.cpr, False)
            if len(cvrs) > 1:
                request.session['cvrs'] = [str(x) for x in cvrs]
                request.session.save()
                return redirect(reverse('aka:choose_cvr')+"?back="+request.get_full_path())
            if len(cvrs) == 1:
                self.cvr = request.session['user_info']['CVR'] = cvrs[0]
            request.session['has_checked_cvr'] = True
            request.session.save()

        try:
            self.cvr = request.session['user_info'].get('CVR')
            self.claimant_ids = self.get_claimants(request)
            self.company = self.get_company(request)
        except (KeyError, TypeError):
            pass

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            'cpr': self.cpr,
            'cvr': self.cvr,
            'claimant_ids': self.claimant_ids,
            'company': self.company,
            'person': self.person,
            'logged_in': {'navn': ' | '.join([
                x['navn'] for x in [self.person, self.company]
                if x is not None
            ])}
        }
        context.update(kwargs)
        return super().get_context_data(**context)


class RequireCprMixin(HasUserMixin):

    def dispatch(self, request, *args, **kwargs):
        try:
            self.cpr = request.session['user_info']['CPR']
        except (KeyError, TypeError):
            raise PermissionDenied('no_cpr')
        return super().dispatch(request, *args, **kwargs)


class RequireCvrMixin(HasUserMixin):

    def dispatch(self, request, *args, **kwargs):
        try:
            self.cvr = request.session['user_info']['CVR']
        except (KeyError, TypeError):
            raise PermissionDenied('no_cvr')
        return super().dispatch(request, *args, **kwargs)


class SimpleGetFormMixin(FormMixin):

    def get(self, request, *args, **kwargs):
        form = self.form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        return super().get(self.request)

    # def form_invalid(self, form):
    #     return super().get(self.request)

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


class IsContentMixin(object):

    def get_context_data(self, **kwargs):
        return super().get_context_data(**dict({
            'is_content': True
        }, **kwargs))


class RendererMixin(object):

    def render(self):
        pass

    @property
    def format(self):
        return self.request.GET.get('format')

    @property
    def accepted_formats(self):
        return []

    @property
    def key(self):
        return self.request.GET.get('key')

    def format_url(self, format, **kwargs):
        params = self.request.GET.copy()
        params['format'] = format
        params.update(kwargs)
        return self.request.path + "?" + params.urlencode()

    def get_context_data(self, **kwargs):
        return super().get_context_data(**dict({
            ("%slink" % format) : self.format_url(format, key=self.key)
            for format in self.accepted_formats
        }, **kwargs))


class PdfRendererMixin(RendererMixin):

    pdf_template_name = ''

    def get_filename(self):
        raise NotImplementedError

    @property
    def accepted_formats(self):
        return super().accepted_formats + ['pdf']

    def render(self):
        if self.format == 'pdf':
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

            html = select_template(self.get_template_names()).render(context)
            # return HttpResponse(html)
            html = html.replace(
                "\"%s" % settings.STATIC_URL,
                "\"file://%s/" % os.path.abspath(settings.STATIC_ROOT)
            )

            pdf = pdfkit.from_string(html, False, options={
                'javascript-delay': 1000,
                'debug-javascript': '',
                'default-header': '',
                'margin-top': '20mm',
                'margin-bottom': '20mm',
                'margin-left': '20mm',
                'margin-right': '20mm',
            })
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = "attachment; filename=\"%s.pdf\"" % self.get_filename()
            return response

        return super().render()

    def get_context_data(self, **kwargs):
        return super().get_context_data(**dict({
            'pdf': self.format == 'pdf'
        }, **kwargs))

    def form_invalid(self, form):
        if self.format == 'pdf':
            return self.render()
        return super().form_invalid(form)


class JsonRendererMixin(RendererMixin):

    @property
    def accepted_formats(self):
        return super().accepted_formats + ['json']

    def render(self):
        if self.format == 'json':
            fields = self.get_fields(self.key)  # List of dicts
            items = self.get_data(self.key)  # List of dicts
            data = {
                'count': len(items),
                'items': [
                    {
                        field['name']: getattr(item, field['name'])
                        for field in fields
                    }
                    for item in items
                ]
            }
            return JsonResponse(data)
        return super().render()


class SpreadsheetRendererMixin(RendererMixin):

    def get_filename(self):
        raise NotImplementedError

    def get_sheetname(self):
        return "Sheet 1"

    def get_extra(self, key):
        return None

    @property
    def accepted_formats(self):
        return super().accepted_formats + ['xlsx', 'ods', 'csv']

    def render(self):
        format = self.format
        if format in self.accepted_formats:
            fields = self.get_fields(self.key)  # List of dicts
            items = self.get_data(self.key)  # List of dicts
            extra = self.get_extra(self.key)  # List of lists
            data = [
                [
                    field.get("title", field['name'])
                    for field in fields
                ]
            ] + [
                [
                    item[field['name']]
                    for field in fields
                ]
                for item in items
            ]

            if extra:
                data += extra

            sheet = excel.pe.Sheet(
                data,
                name=self.get_sheetname(),
                name_columns_by_row=0
            )
            return excel.make_response(
                sheet,
                file_type=format,
                file_name="%s.%s" % (self.get_filename(), format),
            )
        return super().render()
