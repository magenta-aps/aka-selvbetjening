import requests
from aka.helpers.result import Success  # , Error
import zeep
from django.conf import settings
import xmltodict


class PrismeException(Exception):
    def __init__(self, code, text):
        self.code = code
        self.text = text

    def __str__(self):
        return f"Error in response from Prisme. Code: {self.code}, Text: {self.text}"


class PrismeReply(object):
    def __init__(self, status_code, status_text, xml):
        self.status_code = status_code
        self.status_text = status_text
        self.xml = xml


class PrismeReplyObject(object):
    pass


class PrismeClaimant(PrismeReplyObject):
    def __init__(self, xml):
        d = xmltodict.parse(xml)
        self.claimant_id = list(d['FujClaimant']['ClaimantId'])


class PrismeInterestNote(PrismeReplyObject):

    class PrismeInterestJournal(PrismeReplyObject):
        def __init__(self, data):
            self.updated = data['Updated']
            self.account_number = data['AccountNum']
            self.interest_note = data['InterestNote']
            self.to_date = data['ToDate']
            self.billing_classification = data['BillingClassification']
            self.interest_transactions = list([
                PrismeInterestNote.PrismeInterestTransaction(v)
                for k, v in data['CustInterestTransactions'].items()
                if k == 'CustInterestTrans'
            ])

    class PrismeInterestTransaction(PrismeReplyObject):
        def __init__(self, data):
            self.voucher = data['Voucher']
            self.text = data['Txt']
            self.due_date = data['DueDate']
            self.invoice_amount = data['InvoiceAmount']
            self.interest_amount = data['InterestAmount']
            self.transaction_date = data['TransDate']
            self.invoice = data['Invoice']
            self.calculate_from = data['CalcFrom']
            self.calculate_to = data['CalcTo']
            self.interest_days = data['InterestDays']

    def __init__(self, xml):
        data = xmltodict.parse(xml)
        self.cust_interest_journal = [
            PrismeInterestNote.PrismeInterestJournal(x)
            for x in data['CustTable']['CustInterestJour']
        ]


"""
<CustInterestJour>
		<Updated>03-04-2019</Updated>
		<AccountNum>00000725</AccountNum>
		<InterestNote>00000001</InterestNote>
		<ToDate>02-04-2019</ToDate>
		<BillingClassification>200</BillingClassification>
		<CustInterestTransactions>
			<CustInterestTrans>
				<Voucher>FAK-00000040</Voucher>
				<Txt>Renter af fakturanummer 00000044 </Txt>
				<DueDate>02-01-2018</DueDate>
				<InvoiceAmount>4000.00</InvoiceAmount>
				<InterestAmount>160.00</InterestAmount>
				<TransDate>02-01-2018</TransDate>
				<Invoice>00000044</Invoice>
				<CalcFrom>01-01-2019</CalcFrom>
				<CalcTo/>
				<InterestDays>0</InterestDays>
			</CustInterestTrans>
		</CustInterestTransactions>
	</CustInterestJour>
"""


class Prisme():
    '''Class that handles communication with the Prisme system.
    '''

    def __init__(self):
        wsdl = settings.PRISME_CONNECT['wsdl_file']
        self.client = zeep.Client(wsdl=wsdl)

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
        response = self.client.service.getServerVersion(self.create_request_header("getServerVersion"))
        return {'version': response.serverVersion, 'description': response.serverVersionDescription}


    def processService(self, method, xml, reply_container_class):
        request_class = self.client.get_type("tns:GWSRequestDCFUJ")
        request = request_class(
            requestHeader=self.create_request_header(method),
            xmlCollection=self.create_request_body(xml)
        )
        reply = self.client.service.processService(request)
        # reply is of type GWSReplyDCFUJ

        # reply.status is of type GWSReplyStatusDCFUJ
        if reply.status.replyCode != 0:
            raise PrismeException(reply.status.replyCode, reply.staus.replyText)

        # reply_instance if of type GWSReplyInstanceDCFUJ
        outputs = []
        for reply_item in reply.instanceCollection:
            if reply_item.status_code != 0:
                print(f"Something went wrong: {reply_item.status_code}: {reply_item.status_text}")
            else:
                outputs.append(reply_container_class(reply_item.xml))
        return outputs


    def check_cvr(self, cvr_number):
        return self.processService(
            "checkCVR",
            f"<FujClaimant><CvrLegalEntity>{cvr_number}</CvrLegalEntity></FujClaimant>",
            PrismeClaimant
        )


    def get_interest_note(self, customer_id_number, year, month):
        return self.processService(
            "getInterestNote",
            f"<custInterestJour><CustIdentificationNumber>{customer_id_number}</CustIdentificationNumber><YearMonthFUJ>{year:04d}-{month:02d}</YearMonthFUJ></custInterestJour>",
            PrismeInterestNote
        )


    def sendToPrisme(self, data):
        '''Stub
        '''
        return ''

    def receiveFromPrisme(self, url):
        '''Stub
        '''
        return ''

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

    def getRentenota(self, date):
        '''Given a period, will fetch the corresponding rentenote
        from Prisme.

        :param date: Tuple describing (year, month) of rentenota
        :type date: Tuple (string YYYY, string MM)
        :returns: a Result object with the specified data or an error
        '''

        post1 = {'dato': '10/02-18',
                 'postdato': '10/02-18',
                 'bilag': '',
                 'faktura': '',
                 'tekst': '12345678askatrenteMaj',
                 'fradato': '01/05-18',
                 'dage': 31,
                 'grundlag': 1234.00,
                 'val': '',
                 'grundlag2': 12.34,
                 'beloeb': 61.00,
                 }
        post2 = {'dato': '23/03/18',
                 'postdato': '23/03-18',
                 'bilag': 'bilagstekst',
                 'faktura': 'fakturanummer?',
                 'tekst': '12345678askatrenteJuni',
                 'fradato': '01/06-18',
                 'dage': 30,
                 'grundlag': 131.00,
                 'val': '',
                 'grundlag2': 1.31,
                 'beloeb': 1.00,
                 }

        res = {'firmanavn': 'Grønlands Ejendomsselskab ApS',
               'adresse': {
                           'gade': 'H J Rinksvej 29',
                           'postnr': '3900',
                           'by': 'Nuuk',
                           'land': 'Grønland',
                          },
               'poster': [post1, post2]
               }

        return Success(res)

    def getLoentraekDistribution(self, gernummer):
        ''' Given a gernummer, return the previous distribution of 'loentraek'.
        This is used in loentraek, when the user wants to do the same as they
        did last time (I think).

        :param gernummer: GER-nummer
        :type gernummer: ?
        :returns: ?
        '''
        if isinstance(gernummer, str):
            dummypost = {
                         'status': 400,
                         'message': 'Error in communication with Prisme'
                        }
        else:
            dummypost = {'status': 200,
                         'gernummer': gernummer,
                         'traekmaaned': 10,
                         'traekaar': 2018,
                         'data': [
                            {'cprnr': 1010109999,
                             'aftalenummer': 12,
                             'loentraek': 120.0,
                             'nettoloen': 15000
                             }
                            ]
                         }

        return dummypost
