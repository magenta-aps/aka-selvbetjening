import logging
import os
import re
from datetime import date, datetime, time
from decimal import Decimal

import zeep
from aka.exceptions import AkaException
from aka.utils import flatten, get_file_contents_base64
from dict2xml import dict2xml as dict_to_xml
from django.conf import settings
from requests import Session
from requests.auth import HTTPBasicAuth
from requests_ntlm import HttpNtlmAuth
from xmltodict import parse as xml_to_dict
from zeep.exceptions import Fault, TransportError
from zeep.transports import Transport

prisme_settings = settings.PRISME_CONNECT  # type: ignore
logger = logging.getLogger(__name__)


class PrismeException(AkaException):
    title = "prisme.error"
    error_parse = {
        "250": {
            "fordring": [
                {
                    "id": 0,
                    "re": re.compile(
                        r"Der findes ikke en inkassosag med det eksterne ref.nr. (.*)"
                    ),
                    "args": ["refnumber"],
                }
            ],
            "nedskrivning": [
                {
                    "id": 0,
                    "re": re.compile(
                        r"Der findes ikke en inkassosag med det eksterne ref.nr. (.*)"
                    ),
                    "args": ["refnumber"],
                },
                {
                    "id": 1,
                    "re": re.compile(
                        r"Det fremsendte bel\u00f8b (.*) er st\u00f8rre end restsaldoen p\u00e5 inkassosagen (.*)"
                    ),
                    "args": ["amount", "saldo"],
                },
            ],
            "rentenota": [
                {
                    "id": 0,
                    "re": re.compile(
                        r"Der findes ingen renter for dette CPR/CVR (\d+) eller for "
                        r"den angivne periode (\d{2}-\d{2}-\d{4}) (\d{2}-\d{2}-\d{4})"
                    ),
                    "args": ["cvr", "start", "end"],
                },
                {
                    "id": 1,
                    "re": re.compile(r"Der findes ingen debitorer for dette CPR/CVR"),
                    "args": [],
                },
            ],
            "loentraek": [
                {
                    "id": 0,
                    "re": re.compile(r"Aftalenummer (.+) findes ikke"),
                    "args": ["nr"],
                },
                {
                    "id": 1,
                    "re": re.compile(
                        r"Det samme CPR-Nummer (\d+) må kun optræde en gang pr. indberetning"
                    ),
                    "args": ["cpr"],
                },
            ],
            "account": [
                {
                    "id": 0,
                    "re": re.compile(r"Der findes ingen debitorer for dette CPR/CVR"),
                    "args": [],
                }
            ],
        }
    }

    def __init__(self, code, text, context):
        super().__init__(f"prisme.error_{code}", text=text)
        self.code = int(code)
        self.text = text
        self.context = context

        try:
            parsedata = self.error_parse.get(str(code)).get(context)
            if parsedata:
                for p in parsedata:
                    match = p["re"].search(text)
                    if match:
                        for i, argname in enumerate(p["args"], start=1):
                            self.params[argname] = match.group(i)
                        self.error_code = f"{context}.error_{code}.{p['id']}"
                        break
        except Exception as e:
            print("Failed to parse prisme error response: %s" % str(e))
            pass

    @property
    def message(self):
        msg = super().message
        if msg == self.error_code:  # If there is no translated message for this error
            return self.text
        return msg

    def __str__(self):
        return f"Error in response from Prisme. Code: {self.code}, Text: {self.text}"

    @property
    def as_error_dict(self):
        return {"key": self.error_code, "params": self.params}


class PrismeNotFoundException(AkaException):
    pass


class PrismeHttpException(AkaException):
    title = "prisme.http_error"

    def __init__(self, exception):
        error_code = "prisme.http_error"
        params = {}
        if isinstance(exception, TransportError):
            if exception.status_code in (413, 500):
                error_code = f"prisme.http_{exception.status_code}"
            else:
                error_code = f"HTTP {exception.status_code} {exception.message}"
            params["message"] = exception.message
        super().__init__(error_code, **params)


class PrismeServerException(AkaException):
    title = "prisme.generic_error"

    def __init__(self, exception):
        error_code = "prisme.generic_error"
        params = {"message": exception.message}
        super().__init__(error_code, **params)


class PrismeRequestObject(object):
    @property
    def method(self):
        raise NotImplementedError

    @property
    def xml(self):
        raise NotImplementedError

    @property
    def reply_class(self):
        raise NotImplementedError

    @staticmethod
    def prepare(value, is_amount=False):
        if value is None:
            return ""
        if is_amount:
            value = f"{value:.2f}"
        if isinstance(value, datetime):
            value = f"{value:%Y-%m-%dT%H:%M:%S}"
        if isinstance(value, date):
            value = f"{value:%Y-%m-%d}"
        return value

    @staticmethod
    def to_datetime(date):
        return datetime.combine(date, time.min)


class PrismeAccountRequest(PrismeRequestObject):
    wrap = "CustTable"

    # See also choices in KontoForm
    open_closed_map = {0: "Åbne", 1: "Lukkede", 2: "Åbne og Lukkede"}

    def __init__(self, customer_id_number, from_date, to_date, open_closed=2):
        self.customer_id_number = customer_id_number
        self.from_date = from_date
        self.to_date = to_date
        self.open_closed = open_closed

    @property
    def method(self):
        return "getAccountStatementAKI"

    @property
    def xml(self):
        return dict_to_xml(
            {
                "CustIdentificationNumber": self.prepare(self.customer_id_number),
                "FromDate": self.prepare(self.from_date),
                "ToDate": self.prepare(self.to_date),
                "CustInterestCalc": self.open_closed_map[self.open_closed],
            },
            wrap=self.wrap,
        )

    @property
    def reply_class(self):
        return PrismeAccountResponse


class PrismeSELRequest(PrismeAccountRequest):
    @property
    def method(self):
        return "getAccountStatementSEL"

    @property
    def reply_class(self):
        return PrismeSELAccountResponse


class PrismeAKIRequest(PrismeAccountRequest):
    @property
    def method(self):
        return "getAccountStatementAKI"

    @property
    def reply_class(self):
        return PrismeAKIAccountResponse


class PrismeAccountTotalRequest(PrismeRequestObject):
    wrap = "CustTable"

    def __init__(self, customer_id_number):
        self.customer_id_number = customer_id_number

    @property
    def xml(self):
        return dict_to_xml(
            {
                "CustIdentificationNumber": self.prepare(self.customer_id_number),
            },
            wrap=self.wrap,
        )


class PrismeSELTotalRequest(PrismeAccountTotalRequest):
    @property
    def method(self):
        return "getAccountStatementTotalSEL"

    @property
    def reply_class(self):
        return PrismeAccountTotalResponse


class PrismeAKITotalRequest(PrismeAccountTotalRequest):
    @property
    def method(self):
        return "getAccountStatementTotalAKI"

    @property
    def reply_class(self):
        return PrismeAccountTotalResponse


class PrismeClaimRequest(PrismeRequestObject):
    wrap = "CustCollClaimTableFuj"

    def __init__(self, **kwargs):
        self.claimant_id = (kwargs["claimant_id"],)
        self.cpr_cvr = kwargs["cpr_cvr"]
        self.external_claimant = kwargs["external_claimant"]
        self.claim_group_number = kwargs["claim_group_number"]
        self.claim_type = kwargs["claim_type"]
        self.child_cpr = kwargs["child_cpr"]
        self.claim_ref = kwargs["claim_ref"]
        self.amount_balance = float(kwargs["amount_balance"])
        self.text = kwargs["text"]
        self.created_by = kwargs["created_by"]
        self.period_start = kwargs["period_start"]
        self.period_end = kwargs["period_end"]
        self.due_date = kwargs["due_date"]
        self.founded_date = kwargs["founded_date"]
        self.obsolete_date = kwargs["obsolete_date"]
        self.notes = kwargs["notes"]
        self.codebtors = kwargs.get("codebtors", [])
        self.files = [
            (os.path.basename(file.name), get_file_contents_base64(file))
            for file in kwargs.get("files", [])
        ]

    @property
    def method(self):
        return "createClaim"

    @property
    def xml(self):
        # TODO refactor maybe have a list of fields in private attribute instead.
        # Like a mapping between local fields and soap fields?
        return dict_to_xml(
            {
                "CustCollClaimantIdentifier": self.prepare(self.claimant_id),
                "CustCollCprCvr": self.prepare(self.cpr_cvr),
                "CustCollExternalClaimant": self.prepare(self.external_claimant),
                "CustCollClaimGroupNumber": self.prepare(self.claim_group_number),
                "CustCollClaimType": self.prepare(self.claim_type),
                "CustCollChildCprCvr": self.prepare(self.child_cpr),
                "CustCollClaimRef": self.prepare(self.claim_ref),
                "CustCollAmountBalance": self.prepare(
                    self.amount_balance, is_amount=True
                ),
                "CustCollText": self.prepare(self.text),
                "CustCollCreatedBy": self.prepare(self.created_by),
                "CustCollPeriodStart": self.prepare(
                    self.to_datetime(self.period_start)
                ),
                "CustCollPeriodEnd": self.prepare(self.to_datetime(self.period_end)),
                "CustCollDueDate": self.prepare(self.to_datetime(self.due_date)),
                "CustCollFoundedDate": self.prepare(
                    self.to_datetime(self.founded_date)
                ),
                "CustCollObsolescenceDate": self.prepare(
                    self.to_datetime(self.obsolete_date)
                ),
                "Notes": self.prepare(self.notes),
                "coDebtors": [
                    {"coDebtor": {"CustCollCprCvr": self.prepare(codebtor)}}
                    for codebtor in self.codebtors
                ],
                "files": {
                    "file": [
                        {"Name": file[0], "Content": file[1]} for file in self.files
                    ]
                },
            },
            wrap=self.wrap,
        )

    @property
    def reply_class(self):
        return PrismeClaimResponse


class PrismeImpairmentRequest(PrismeRequestObject):
    wrap = "CustCollClaimTableFuj"

    def __init__(
        self, claimant_id, cpr_cvr, claim_ref, amount_balance, claim_number_seq
    ):
        self.claimant_id = claimant_id
        self.cpr_cvr = cpr_cvr
        self.claim_ref = claim_ref
        self.amount_balance = amount_balance
        self.claim_number_seq = claim_number_seq

    @property
    def method(self):
        return "createImpairment"

    @property
    def xml(self):
        return dict_to_xml(
            {
                "CustCollClaimantIdentifier": self.prepare(self.claimant_id),
                "CustCollCprCvr": self.prepare(self.cpr_cvr),
                "CustCollClaimRef": self.prepare(self.claim_ref),
                "CustCollAmountBalance": self.prepare(
                    self.amount_balance, is_amount=True
                ),
                "CustCollClaimNumberSeq": self.prepare(self.claim_number_seq),
            },
            wrap=self.wrap,
        )

    @property
    def reply_class(self):
        return PrismeImpairmentResponse


class PrismeCvrCheckRequest(PrismeRequestObject):
    wrap = "FujClaimant"

    def __init__(self, cvr):
        self.cvr = cvr

    @property
    def method(self):
        return "checkCVR"

    @property
    def xml(self):
        return dict_to_xml({"CvrLegalEntity": self.cvr}, wrap=self.wrap, newlines=False)

    @property
    def reply_class(self):
        return PrismeCvrCheckResponse


class PrismeInterestNoteRequest(PrismeRequestObject):
    wrap = "custInterestJour"

    def __init__(self, customer_id_number, year, month):
        self.customer_id_number = customer_id_number
        self.year = int(year)
        self.month = int(month)

    @property
    def method(self):
        return "getInterestNote"

    @property
    def xml(self):
        return dict_to_xml(
            {
                "CustIdentificationNumber": self.customer_id_number,
                "YearMonthFUJ": f"{self.year:04d}-{self.month:02d}",
            },
            wrap=self.wrap,
        )

    @property
    def reply_class(self):
        return PrismeInterestNoteResponse


class PrismePayrollRequest(PrismeRequestObject):
    wrap = "custPayRollFromEmployerHeader"

    def __init__(self, cvr, date, received_date, amount, lines):
        self.cvr = cvr
        self.date = date
        self.received_date = received_date
        self.amount = amount
        if type(lines) is not list:
            lines = [lines]
        self.lines = lines

    @property
    def method(self):
        return "createPayrollFromEmployer"

    @property
    def xml(self):
        return dict_to_xml(
            {
                "GERCVR": self.cvr,
                "Date": self.prepare(self.to_datetime(self.date)),
                "ReceivedDate": self.prepare(self.to_datetime(self.received_date)),
                "TotalAmount": self.prepare(self.amount, is_amount=True),
                "custPayRollFromEmployerLines": {
                    PrismePayrollRequestLine.wrap: [line.dict for line in self.lines]
                },
            },
            wrap=self.wrap,
        )

    @property
    def reply_class(self):
        return PrismePayrollResponse


class PrismePayrollRequestLine(PrismeRequestObject):
    wrap = "custPayRollFromEmployerLine"

    def __init__(self, cpr_cvr, agreement_number, amount, net_salary):
        self.cpr_cvr = cpr_cvr
        self.agreement_number = agreement_number
        self.amount = amount
        self.net_salary = net_salary

    @property
    def dict(self):
        return {
            "CprCvrEntity": self.prepare(self.cpr_cvr),
            "AgreementNumber": self.prepare(self.agreement_number),
            "Amount": self.prepare(self.amount, is_amount=True),
            "NetSalary": self.prepare(self.net_salary, is_amount=True),
        }

    @property
    def xml(self):
        return dict_to_xml(self.dict, wrap=self.wrap)


class PrismeResponseObject(object):
    def __init__(self, request, xml):
        self.request = request
        self.xml = xml


class PrismeAccountResponseTransaction(object):
    def __init__(self, data):
        self.account_number = data["AccountNum"]
        self.transaction_date = data["TransDate"]
        self.accounting_date = data["AccountingDate"]
        self.debitor_group_id = data["CustGroup"]
        self.debitor_group_name = data["CustGroupName"]
        self.voucher = data["Voucher"]
        self.text = data["Txt"]
        self.payment_code = data["CustPaymCode"]
        self.payment_code_name = data["CustPaymDescription"]
        amount = data["AmountCur"]
        try:
            self.amount = Decimal(amount)
        except ValueError:
            self.amount = 0
        self.remaining_amount = data["RemainAmountCur"]
        try:
            self.remaining_amount = Decimal(self.remaining_amount)
        except ValueError:
            self.remaining_amount = 0
        self.due_date = data["DueDate"]
        self.closed_date = data["Closed"]
        self.last_settlement_voucher = data["LastSettleVoucher"]
        self.collection_letter_date = data["CollectionLetterDate"]
        self.collection_letter_code = data["CollectionLetterCode"]
        self.claim_type_code = data["ClaimTypeCode"]
        self.invoice_number = data["Invoice"]
        self.transaction_type = data["TransType"]


class PrismeAccountResponse(PrismeResponseObject):
    itemclass = PrismeAccountResponseTransaction

    def __init__(self, request, xml):
        super(PrismeAccountResponse, self).__init__(request, xml)
        if xml is None:
            self.transactions = []
        else:
            data = xml_to_dict(xml)
            transactions = data["CustTable"]["CustTrans"]
            if type(transactions) is not list:
                transactions = [transactions]
            self.transactions = [self.itemclass(x) for x in transactions]

    def __iter__(self):
        yield from self.transactions

    def __len__(self):
        return len(self.transactions)


class PrismeEmployerAccountResponseTransaction(PrismeAccountResponseTransaction):
    def __init__(self, data):
        super().__init__(data)
        self.rate_number = data.get("RateNmb")
        self.child_claimant = data.get("ChildClaimantFuj") or data.get("ChildClaimant")


class PrismeSELAccountResponse(PrismeAccountResponse):
    itemclass = PrismeEmployerAccountResponseTransaction


class PrismeCitizenAccountResponseTransaction(PrismeAccountResponseTransaction):
    def __init__(self, data):
        super().__init__(data)
        self.claimant_name = data["ClaimantName"]
        self.claimant_id = data["ClaimantId"]
        self.child_claimant = data.get("ChildClaimant") or data.get("ChildClaimantFuj")


class PrismeAKIAccountResponse(PrismeAccountResponse):
    itemclass = PrismeCitizenAccountResponseTransaction


class PrismeAccountTotalResponse(PrismeResponseObject):
    def __init__(self, request, xml):
        super(PrismeAccountTotalResponse, self).__init__(request, xml)
        data = xml_to_dict(xml)["CustTable"]
        self.total_claim = data["TotalClaim"]
        self.total_payment = data["TotalPayment"]
        self.total_sum = data["TotalSum"]
        self.total_restance = data["TotalRestance"]


class PrismeRecIdResponse(PrismeResponseObject):
    response_tag = ""

    def __init__(self, request, xml):
        super(PrismeRecIdResponse, self).__init__(request, xml)
        d = xml_to_dict(xml)
        self.rec_id = d[self.response_tag]["RecId"]

    @classmethod
    def test(cls, rec_id):
        return cls(
            None, f"<{cls.response_tag}><RecId>{rec_id}</RecId></{cls.response_tag}>"
        )


class PrismeClaimResponse(PrismeRecIdResponse):
    response_tag = "CustCollClaimTableFuj"


class PrismeImpairmentResponse(PrismeRecIdResponse):
    response_tag = "CustCollClaimTableFuj"


class PrismePayrollResponse(PrismeRecIdResponse):
    response_tag = "CustPayrollFromEmployerHeaderFUJ"


class PrismeCvrCheckResponse(PrismeResponseObject):
    def __init__(self, request, xml):
        super(PrismeCvrCheckResponse, self).__init__(request, xml)
        d = xml_to_dict(xml)
        if d.get("FujClaimant") is None or d["FujClaimant"].get("ClaimantId") is None:
            raise PrismeNotFoundException("prisme.cvrcheck_no_result", cvr=request.cvr)
        self.claimant_id = flatten(d["FujClaimant"]["ClaimantId"])


class PrismeInterestNoteResponse(PrismeResponseObject):
    def __init__(self, request, xml):
        super(PrismeInterestNoteResponse, self).__init__(request, xml)
        data = xml_to_dict(xml)
        journals = data["CustTable"]["CustInterestJour"]
        if type(journals) is not list:
            journals = [journals]
        self.interest_journal = [PrismeInterestResponseJournal(x) for x in journals]


class PrismeInterestResponseJournal(object):
    def __init__(self, data):
        self.updated = data["Updated"]
        self.account_number = data["AccountNum"]
        self.interest_note = data["InterestNote"]
        self.to_date = data["ToDate"]
        self.billing_classification = data["BillingClassification"]
        self.interest_transactions = []
        for k, v in data["CustInterestTransactions"].items():
            if k == "CustInterestTrans":
                if type(v) is not list:
                    v = [v]
                for transaction in v:
                    self.interest_transactions.append(
                        PrismeInterestNoteResponseTransaction(transaction)
                    )
        self.data = data


class PrismeInterestNoteResponseTransaction(object):
    def __init__(self, data):
        self.voucher = data["Voucher"]
        self.invoice = data["Invoice"]
        self.text = data["Txt"]
        self.invoice_amount = data["InvoiceAmount"]
        self.interest_amount = data["InterestAmount"]
        self.due_date = data["DueDate"]
        self.transaction_date = data["TransDate"]
        self.calculate_from_date = data["CalcFrom"]
        self.calculate_to_date = data["CalcTo"]
        self.interest_days = data["InterestDays"]
        self.data = data


class Prisme(object):
    _client = None

    def __init__(self):
        self.mock = prisme_settings.get("mock", False)
        self.mock_data = prisme_settings.get("mock_data", {})

    @property
    def client(self):
        if self._client is None and self.mock is False:
            wsdl = prisme_settings["wsdl_file"]
            session = Session()
            if "proxy" in prisme_settings:
                if "socks" in prisme_settings["proxy"]:
                    proxy = f'socks5://{prisme_settings["proxy"]["socks"]}'
                    session.proxies = {"http": proxy, "https": proxy}

            auth_settings = prisme_settings.get("auth")
            if auth_settings:
                if "basic" in auth_settings:
                    basic_settings = auth_settings["basic"]
                    session.auth = HTTPBasicAuth(
                        f'{basic_settings["username"]}@{basic_settings["domain"]}',
                        basic_settings["password"],
                    )
                elif "ntlm" in auth_settings:
                    ntlm_settings = auth_settings["ntlm"]
                    session.auth = HttpNtlmAuth(
                        f"{ntlm_settings['domain']}\\{ntlm_settings['username']}",
                        ntlm_settings["password"],
                    )
            try:
                self._client = zeep.Client(
                    wsdl=wsdl,
                    transport=Transport(
                        session=session, timeout=3600, operation_timeout=3600
                    ),
                )
            except Exception as e:
                print("Failed connecting to prisme: %s" % str(e))
                raise e
            self._client.set_ns_prefix(
                "tns", "http://schemas.datacontract.org/2004/07/Dynamics.Ax.Application"
            )
        return self._client

    def create_request_header(self, method, area="SULLISSIVIK", client_version=1):
        request_header_class = self.client.get_type("tns:GWSRequestHeaderDCFUJ")
        return request_header_class(
            clientVersion=client_version, area=area, method=method
        )

    def create_request_body(self, xml):
        if type(xml) is not list:
            xml = [xml]
        item_class = self.client.get_type("tns:GWSRequestXMLDCFUJ")
        container_class = self.client.get_type("tns:ArrayOfGWSRequestXMLDCFUJ")
        return container_class(list([item_class(xml=x) for x in xml]))

    def get_server_version(self):
        response = self.client.service.getServerVersion(
            self.create_request_header("getServerVersion")
        )
        return {
            "version": response.serverVersion,
            "description": response.serverVersionDescription,
        }

    def process_service(self, request_object, context, cpr, cvr):
        try:
            logger.info(
                "CPR=%s CVR=%s Sending to %s:\n%s"
                % (cpr, cvr, request_object.method, request_object.xml)
            )

            outputs = []
            if self.mock is True:
                xml = self.mock_data.get(request_object.__class__.__name__)
                if xml:
                    outputs.append(request_object.reply_class(request_object, xml))
                return outputs

            request_class = self.client.get_type("tns:GWSRequestDCFUJ")
            request = request_class(
                requestHeader=self.create_request_header(request_object.method),
                xmlCollection=self.create_request_body(request_object.xml),
            )
            # reply is of type GWSReplyDCFUJ
            reply = self.client.service.processService(request)

            # reply.status is of type GWSReplyStatusDCFUJ
            if reply.status.replyCode != 0:
                raise PrismeException(
                    reply.status.replyCode, reply.status.replyText, context
                )

            # reply_item is of type GWSReplyInstanceDCFUJ
            for reply_item in reply.instanceCollection.GWSReplyInstanceDCFUJ:
                if reply_item.replyCode == 0:
                    logger.info(
                        "CPR=%s CVR=%s Receiving from %s:\n%s"
                        % (cpr, cvr, request_object.method, reply_item.xml)
                    )
                    outputs.append(
                        request_object.reply_class(request_object, reply_item.xml)
                    )
                else:
                    raise PrismeException(
                        reply_item.replyCode, reply_item.replyText, context
                    )
            return outputs
        except TransportError as e:
            raise PrismeHttpException(e)
        except Fault as e:
            raise PrismeServerException(e)
        except Exception as e:
            logger.info(
                "CPR=%s CVR=%s Error in process_service for %s: %s %s"
                % (cpr, cvr, request_object.method, str(type(e)), str(e))
            )
            raise e

    def check_cvr(self, cvr):
        response = self.process_service(
            PrismeCvrCheckRequest(cvr), "cvrcheck", None, cvr
        )
        return response[0].claimant_id
