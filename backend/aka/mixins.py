import json
import os

import pdfkit
from aka.clients.dafo import Dafo
from aka.clients.prisme import PrismeCvrCheckRequest, Prisme
from aka.clients.prisme import PrismeNotFoundException
from aka.exceptions import AkaException
from aka.utils import flatten
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.template.loader import select_template
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
                print(Prisme().process_service(PrismeCvrCheckRequest(cvr), 'cvr_check'))
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
            self.cvr = request.session['user_info'].get('CVR')
            self.claimant_ids = self.get_claimants(request)
            self.company = self.get_company(request)
        except (KeyError, TypeError):
            pass

        try:
            self.cpr = request.session['user_info']['CPR']
            self.person = {'navn': request.session['user_info']['name']}
            self.p = self.get_person(request)
        except (KeyError, TypeError):
            pass

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            'cpr': self.cpr,
            'cvr': self.cvr,
            'claimant_ids': self.claimant_ids,
            'company': self.company,
            'person': self.person
        }
        context.update(kwargs)
        return super().get_context_data(**context)


class RequireCprMixin(HasUserMixin):
    def dispatch(self, request, *args, **kwargs):

        # self.cpr = '0101601919'
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
        response['Content-Disposition'] = "attachment; filename=\"%s\"" % filename
        return response

    def get_context_data(self, **kwargs):
        full_path = self.request.get_full_path_info()
        full_path += ('&' if '?' in full_path else '?') + 'format=pdf'
        context = {
            'pdf': self.request.GET.get('format') == 'pdf',
            'pdflink': full_path
        }
        context.update(kwargs)
        return super().get_context_data(**context)
