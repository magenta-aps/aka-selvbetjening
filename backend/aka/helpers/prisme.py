import os

import requests
import zeep
from dict2xml import dict2xml as dict_to_xml
from django.conf import settings
from requests import Session
from requests_ntlm import HttpNtlmAuth
from xmltodict import parse as xml_to_dict
from datetime import date

from zeep.transports import Transport


class PrismeException(Exception):
    def __init__(self, code, text):
        self.code = code
        self.text = text

    def __str__(self):
        return f"Error in response from Prisme. Code: {self.code}, Text: {self.text}"


class PrismeRequestObject(object):

    @property
    def method(self):
        raise NotImplementedError

    @property
    def xml(self):
        raise NotImplementedError

    @staticmethod
    def prepare(value, is_amount=False):
        if value is None:
            return ''
        if is_amount:
            value = f"{value:.2f}"
        if isinstance(value, date):
            value = f'{value:%Y-%m-%d}T00:00:00'
        return value


class PrismeClaimRequest(PrismeRequestObject):

    def __init__(self, claimant_id, cpr_cvr, external_claimant, claim_group_number, claim_type, child_cpr_cvr, claim_ref, amount_balance, text, created_by, period_start, period_end, due_date, founded_date, obsolete_date, notes, codebtors=[], files=[]):
        self.claimant_id = claimant_id,
        self.cpr_cvr = cpr_cvr
        self.external_claimant = external_claimant
        self.claim_group_number = claim_group_number
        self.claim_type = claim_type
        self.child_cpr_cvr = child_cpr_cvr
        self.claim_ref = claim_ref
        self.amount_balance = float(amount_balance)
        self.text = text
        self.created_by = created_by
        self.period_start = period_start
        self.period_end = period_end
        self.due_date = due_date
        self.founded_date = founded_date
        self.obsolete_date = obsolete_date
        self.notes = notes
        self.codebtors = codebtors
        self.files = []
        for file in files:
            self.files.append((
                os.path.basename(file.name),
                AKAUtils.get_file_contents_base64(file)
            ))

    @property
    def method(self):
        return 'createClaim'

    @property
    def xml(self):
        return dict_to_xml({
            'CustCollClaimantIdentifier': self.prepare(self.claimant_id),
            'CustCollCprCvr': self.prepare(self.cpr_cvr),
            'CustCollExternalClaimant': self.prepare(self.external_claimant),
            'CustCollClaimGroupNumber': self.prepare(self.claim_group_number),
            'CustCollClaimType': self.prepare(self.claim_type),
            'CustCollChildCprCvr': self.prepare(self.child_cpr_cvr),
            'CustCollClaimRef': self.prepare(self.claim_ref),
            'CustCollAmountBalance': self.prepare(self.amount_balance, is_amount=True),
            'CustCollText': self.prepare(self.text),
            'CustCollCreatedBy': self.prepare(self.created_by),
            'CustCollPeriodStart': self.prepare(self.period_start),
            'CustCollPeriodEnd': self.prepare(self.period_end),
            'CustCollDueDate': self.prepare(self.due_date),
            'CustCollFoundedDate': self.prepare(self.founded_date),
            'CustCollObsolescenceDate': self.prepare(self.obsolete_date),
            'Notes': self.prepare(self.notes),
            'coDebtors': [
                {'coDebtor': {'CustCollCprCvr': self.prepare(codebtor)}}
                for codebtor in self.codebtors
            ],
            'files': [
                {
                    'file': {
                        'Name': file[0],
                        'Content': file[1]
                    }
                }
                for file in self.files
            ]
        }, wrap="CustCollClaimTableFuj")


class PrismeImpairmentRequest(PrismeRequestObject):

    def __init__(self, claimant_id, cpr_cvr, claim_ref, amount_balance, claim_number_seq):
        self.claimant_id = claimant_id
        self.cpr_cvr = cpr_cvr
        self.claim_ref = claim_ref
        self.amount_balance = amount_balance
        self.claim_number_seq = claim_number_seq

    @property
    def method(self):
        return 'createClaim'

    @property
    def xml(self):
        return dict_to_xml({
            'CustCollClaimantIdentifier': self.prepare(self.claimant_id),
            'CustCollCprCvr': self.prepare(self.cpr_cvr),
            'CustCollClaimRef': self.prepare(self.claim_ref),
            'CustCollAmountBalance': self.prepare(self.amount_balance, is_amount=True),
            'CustCollClaimNumberSeq': self.prepare(self.claim_number_seq)
        }, wrap='CustCollClaimTableFuj')


class PrismeCvrCheckRequest(PrismeRequestObject):

    def __init__(self, cvr):
        self.cvr = cvr

    @property
    def method(self):
        return 'checkCVR'

    @property
    def xml(self):
        return dict_to_xml({
            'CvrLegalEntity': self.cvr
        }, wrap='FujClaimant')


class PrismeInterestNoteRequest(PrismeRequestObject):

    def __init__(self, customer_id_number, year, month):
        self.customer_id_number = customer_id_number
        self.year = int(year)
        self.month = int(month)

    @property
    def method(self):
        return 'getInterestNote'

    @property
    def xml(self):
        return dict_to_xml({
            'CustIdentificationNumber': self.customer_id_number,
            'YearMonthFUJ': f"{self.year:04d}-{self.month:02d}"
        }, wrap='custInterestJour')


class PrismeResponseObject(object):
    pass


class PrismeClaimResponse(PrismeResponseObject):
    def __init__(self, xml):
        d = xml_to_dict(xml)
        self.rec_id = d['CustCollClaimTableFuj']['RecId']


class PrismeImpairmentResponse(PrismeClaimResponse):
    pass


class PrismeCvrCheckResponse(PrismeResponseObject):
    def __init__(self, xml):
        d = xml_to_dict(xml)
        self.claimant_id = list(d['FujClaimant']['ClaimantId'])


class PrismeInterestNoteResponse(PrismeResponseObject):

    class PrismeInterestJournal(PrismeResponseObject):
        def __init__(self, data):
            self.updated = data['Updated']
            self.account_number = data['AccountNum']
            self.interest_note = data['InterestNote']
            self.to_date = data['ToDate']
            self.billing_classification = data['BillingClassification']
            self.interest_transactions = list([
                PrismeInterestNoteResponse.PrismeInterestTransaction(v)
                for k, v in data['CustInterestTransactions'].items()
                if k == 'CustInterestTrans'
            ])
            self.data = data

    class PrismeInterestTransaction(PrismeResponseObject):
        def __init__(self, data):
            self.voucher = data['Voucher']
            self.invoice = data['Invoice']
            self.text = data['Txt']
            self.invoice_amount = data['InvoiceAmount']
            self.interest_amount = data['InterestAmount']
            self.due_date = data['DueDate']
            self.transaction_date = data['TransDate']
            self.calculate_from_date = data['CalcFrom']
            self.calculate_to_date = data['CalcTo']
            self.interest_days = data['InterestDays']
            self.data = data

    def __init__(self, xml):
        data = xml_to_dict(xml)
        self.interest_journal = [
            PrismeInterestNoteResponse.PrismeInterestJournal(x)
            for x in data['CustTable']['CustInterestJour']
        ]


class Prisme(object):

    def __init__(self, request=None, testing=None):
        prisme_settings = settings.PRISME_CONNECT
        wsdl = prisme_settings['wsdl_file']
        if request is not None:
            self.testing = request.GET.get('testing') == '1'
        if testing is not None:
            self.testing = testing

        session = Session()

        if 'proxy' in prisme_settings:
            if 'socks' in prisme_settings['proxy']:
                proxy = f'socks5://{prisme_settings["proxy"]["socks"]}'
                session.proxies = {'http': proxy, 'https': proxy}

        auth_settings = prisme_settings.get('auth')
        if auth_settings:
            if 'basic' in auth_settings:
                basic_settings = auth_settings['basic']
                session.auth = (
                    f'{basic_settings["username"]}@{basic_settings["domain"]}',
                    basic_settings["password"]
                )
            elif 'ntlm' in auth_settings:
                ntlm_settings = auth_settings['ntlm']
                session.auth = HttpNtlmAuth(
                    f"{ntlm_settings['domain']}\\{ntlm_settings['username']}",
                    ntlm_settings['password']
                )

        self.client = zeep.Client(
            wsdl=wsdl,
            transport=Transport(
                session=session
            )
        )
        self.client.set_ns_prefix("tns", 'http://schemas.datacontract.org/2004/07/Dynamics.Ax.Application')

    def create_request_header(self, method, area="SULLISSIVIK", client_version=1):
        request_header_class = self.client.get_type('tns:GWSRequestHeaderDCFUJ')
        return request_header_class(
            clientVersion=client_version,
            area=area,
            method=method
        )

    def create_request_body(self, xml):
        if type(xml) is not list:
            xml = [xml]
        item_class = self.client.get_type("tns:GWSRequestXMLDCFUJ")
        container_class = self.client.get_type("tns:ArrayOfGWSRequestXMLDCFUJ")
        return container_class(list([
            item_class(xml=x) for x in xml
        ]))

    def getServerVersion(self):
        response = self.client.service.getServerVersion(
            self.create_request_header("getServerVersion")
        )
        return {
            'version': response.serverVersion,
            'description': response.serverVersionDescription
        }

    def processService(self, method, xml, reply_container_class):
        request_class = self.client.get_type("tns:GWSRequestDCFUJ")
        request = request_class(
            requestHeader=self.create_request_header(method),
            xmlCollection=self.create_request_body(xml)
        )
        # reply is of type GWSReplyDCFUJ
        reply = self.client.service.processService(request)

        # reply.status is of type GWSReplyStatusDCFUJ
        if reply.status.replyCode != 0:
            raise PrismeException(reply.status.replyCode, reply.status.replyText)

        outputs = []
        # reply_item if of type GWSReplyInstanceDCFUJ
        for reply_item in reply.instanceCollection.GWSReplyInstanceDCFUJ:
            if reply_item.replyCode == 0:
                outputs.append(reply_container_class(reply_item.xml))
            else:
                raise Exception(
                    f"Prisme error {reply_item.replyCode}:"
                    f" {reply_item.replyText}"
                )
        return outputs

    def create_claim(self, claim):
        if not isinstance(claim, PrismeClaimRequest):
            raise Exception("claim must be of type PrismeClaim")
        if self.testing:
            return [
                PrismeClaimResponse(
                    AKAUtils.get_file_contents('aka/tests/claim_response.xml')
                )
            ]
        return self.processService(
            "createClaim",
            claim.xml,
            PrismeClaimResponse
        )

    def create_impariment(self, impairment):
        if not isinstance(impairment, PrismeImpairmentRequest):
            raise Exception("impairment must be of type PrismeImpairment")
        return self.processService(
            impairment.method,
            impairment.xml,
            PrismeImpairmentResponse
        )

    def check_cvr(self, cvr_check):
        if not isinstance(cvr_check, PrismeCvrCheckRequest):
            raise Exception("cvr_check must be of type PrismeCvrCheckRequest")
        return self.processService(
            cvr_check.method,
            cvr_check.xml,
            PrismeCvrCheckResponse
        )

    def get_interest_note(self, interestnote_req):
        if not isinstance(interestnote_req, PrismeInterestNoteRequest):
            raise Exception(
                "interestnote_req must be of type PrismeInterestNoteRequest"
            )
        return self.processService(
            interestnote_req.method,
            interestnote_req.xml,
            PrismeInterestNoteResponse
        )


    def fetchPrismeFile(self, url, localfilename):
        '''
        Fetches a file from url, and stores it in destfolder with the name
        given as the last part of the url.

        :param url: Where to get the file from.
        :type url: string.
        :param localfilename: Full path and name of the file on this server,
                              i.e. after we fetch and store it.
        :type localfilename: string.
        :returns: True if OK, else False.
        '''

        request = requests.get(url, stream=True)

        if request.status_code != requests.codes.ok:
            return False

        with open(localfilename, 'wb+') as destination:
            for block in request.iter_content(1024 * 8):
                if block:
                    destination.write(block)

        return True
