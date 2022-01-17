import logging
from datetime import date

from aka.clients.prisme import PrismeClaimRequest
from aka.clients.prisme import PrismeClaimResponse
from aka.tests.mixins import TestMixin
from aka.utils import dummy_management_form
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings, TestCase
from lxml import etree
from xmltodict import parse as xml_to_dict


@override_settings(OPENID_CONNECT={'enabled': False}, NEMID_CONNECT={'enabled': False})
class BasicTestCase(TestMixin, TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        session = self.client.session
        session['user_info'] = {'CVR': '12479182'}
        session.save()
        super(BasicTestCase, self).setUp()
        self.prisme_return = {
            'PrismeClaimRequest': PrismeClaimResponse(None, "<CustCollClaimTableFuj><RecId>1234</RecId></CustCollClaimTableFuj>")
        }

    # PRISME INTERFACE TESTS

    def test_create_claim_request_parse(self):
        attachment = File(open('aka/tests/resources/testfile.pdf'))
        attachment.close()
        request = PrismeClaimRequest(
            claimant_id="32SE",
            cpr_cvr="0102030405",
            external_claimant="Ekstern fordringshaver",
            claim_group_number=4,
            claim_type=1,
            child_cpr=None,
            claim_ref=1234,
            amount_balance=20,
            text="Udlæg for hotdog",
            created_by="TesterPerson",
            period_start=date(2019, 3, 7),
            period_end=date(2019, 3, 8),
            due_date=date(2019, 4, 1),
            founded_date=date(2019, 3, 7),
            obsolete_date=date(2019, 5, 1),
            notes="Den smagte godt",
            codebtors=[11223344, 55667788],
            files=[attachment]
        )
        self.compare(
            xml_to_dict(self.get_file_contents('aka/tests/resources/claim_request.xml')),
            xml_to_dict(request.xml),
            ""
        )

    def test_create_claim_response_parse(self):
        response = PrismeClaimResponse(None, self.get_file_contents('aka/tests/resources/claim_response.xml'))
        self.assertEqual("5637238342", response.rec_id)

    # POSITIVE TESTS

    def test_claim_success_1(self):
        # Contains just the required fields
        formData = {
            'fordringshaver': 'test-fordringshaver',
            'debitor': 'test-debitor',
            'fordringsgruppe': '14',
            'fordringstype': '16.5',
            'periodestart': date(2019, 3, 28).strftime("%d/%m/%Y"),
            'periodeslut': date(2019, 3, 28).strftime("%d/%m/%Y"),
            'forfaldsdato': date(2019, 3, 28).strftime("%d/%m/%Y"),
            'betalingsdato': date(2019, 3, 28).strftime("%d/%m/%Y"),
            'foraeldelsesdato': date(2019, 5, 28).strftime("%d/%m/%Y"),
            'hovedstol': 100,
            'hovedstol_posteringstekst': 'Testing',
            'kontaktperson': 'Test Testersen',
            'form-0-cpr': '1234567890',
            'ekstern_sagsnummer': '1234'
        }
        for management_field, value in {
            'TOTAL_FORMS': 1, 'INITIAL_FORMS': 0, 'MIN_NUM_FORMS': 0, 'MAX_NUM_FORMS': 1000
        }.items():
            formData["form-%s" % management_field] = str(value)
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        el = root.xpath("//ul[@class='success-list']/li")
        self.assertEqual(1, len(el))
        self.assertEqual('1234', el[0].text)

    def test_claim_success_2(self):
        # Contains all required fields, and some more
        self.service_mock.return_value = [
            PrismeClaimResponse(None, "<CustCollClaimTableFuj><RecId>1234</RecId></CustCollClaimTableFuj>")
        ]
        formData = {
            'fordringshaver': 'test-fordringshaver',
            'debitor': 'test-debitor',
            'fordringsgruppe': '14',
            'fordringstype': '16.5',
            'fordringshaver2': 'test-fordringshaver2',
            'periodestart': date(2019, 3, 27).strftime("%d/%m/%Y"),
            'periodeslut': date(2019, 3, 28).strftime("%d/%m/%Y"),
            'forfaldsdato': date(2019, 3, 28).strftime("%d/%m/%Y"),
            'betalingsdato': date(2019, 3, 28).strftime("%d/%m/%Y"),
            'foraeldelsesdato': date(2019, 5, 28).strftime("%d/%m/%Y"),
            'hovedstol': 100,
            'hovedstol_posteringstekst': 'Testing',
            'kontaktperson': 'Test Testersen',
            'form-0-cpr': '1234567890',
            'ekstern_sagsnummer': '1234'
        }
        for management_field, value in {
            'TOTAL_FORMS': 1, 'INITIAL_FORMS': 0, 'MIN_NUM_FORMS': 0, 'MAX_NUM_FORMS': 1000
        }.items():
            formData["form-%s" % management_field] = str(value)
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        el = root.xpath("//ul[@class='success-list']/li")
        self.assertEqual(1, len(el))
        self.assertEqual('1234', el[0].text)

    def test_claim_upload_success(self):
        # Contains all required fields, and some more
        fp = open('aka/tests/resources/inkasso.csv', "rb")
        uploadfile = SimpleUploadedFile(
            'test.csv',
            fp.read(),
            content_type="text/csv"
        )
        fp.close()
        formData = {
            'file': uploadfile
        }
        response = self.client.post('/inkassosag/upload/', formData)
        root = etree.fromstring(response.content, etree.HTMLParser())
        el = root.xpath("//ul[@class='success-list']/li")
        self.assertEqual(2, len(el))
        self.assertEqual('1234', el[0].text)
        self.assertEqual('1234', el[1].text)

    # NEGATIVE TESTS

    def test_claim_missing_fields_1(self):
        # Does not contain all required fields
        formData = {
            'fordringshaver2': 'test-fordringshaver2',
            'debitor': 'test-debitor',
            'fordringsgruppe': '1',
            'fordringstype': '1',
            'fordringsgruppe_id': '3',
            'periodestart': date(2019, 3, 27),
            'periodeslut': date(2019, 3, 28)
        }
        formData.update(dummy_management_form("form"))
        response = self.client.post(self.url, formData)
        root = etree.fromstring(response.content, etree.HTMLParser())
        for field in ['hovedstol', 'forfaldsdato', 'betalingsdato', 'foraeldelsesdato']:
            erroritems = root.xpath("//div[@data-field='id_%s']//ul[@class='errorlist']/li" % field)
            self.assertEqual(1, len(erroritems))
            self.assertEqual('error.required', erroritems[0].attrib.get('data-trans'))

    def test_claim_missing_fields_2(self):
        # Test that multiple errors are recieved
        formData = {
            'fordringshaver2': 'test-fordringshaver2',
            'fordringsgruppe': '1',
            'fordringstype': '1',
            'fordringsgruppe_id': '3',
            'periodestart': date(2019, 3, 27),
            'periodeslut': date(2019, 3, 28)
        }
        formData.update(dummy_management_form("form"))
        response = self.client.post(self.url, formData)
        root = etree.fromstring(response.content, etree.HTMLParser())
        for field in ['debitor', 'hovedstol', 'forfaldsdato', 'betalingsdato', 'foraeldelsesdato']:
            erroritems = root.xpath("//div[@data-field='id_%s']//ul[@class='errorlist']/li" % field)
            self.assertEqual(1, len(erroritems))
            self.assertEqual('error.required', erroritems[0].attrib.get('data-trans'))

    def test_claim_incorrect_group_and_type(self):
        # Test fordringsgruppe and -type errors
        formData = {
            'fordringshaver2': 'test-fordringshaver2',
            'fordringshaver': 'test-fordringshaver',
            'debitor': 'test-debitor',
            'fordringsgruppe': '100',
            'fordringstype': '100',
            'fordringsgruppe_id': '13',
            'periodestart': date(2019, 3, 27),
            'periodeslut': date(2019, 3, 28)
        }
        formData.update(dummy_management_form("form"))
        response = self.client.post(self.url, formData)
        root = etree.fromstring(response.content, etree.HTMLParser())
        expected = {
            'fordringsgruppe': 'error.fordringsgruppe_not_found',
            'fordringstype': 'error.fordringstype_not_found'
        }
        expected.update({
            field: 'error.required'
            for field in ['hovedstol', 'forfaldsdato', 'betalingsdato', 'foraeldelsesdato']
        })
        for field, message in expected.items():
            erroritems = root.xpath("//div[@data-field='id_%s']//ul[@class='errorlist']/li" % field)
            self.assertEqual(1, len(erroritems))
            self.assertEqual(message, erroritems[0].attrib.get('data-trans'))

    def test_claim_incorrect_group(self):
        # Test fordringsgruppe and -type errors
        formData = {
            'fordringshaver2': 'test-fordringshaver2',
            'fordringshaver': 'test-fordringshaver',
            'debitor': 'test-debitor',
            'fordringsgruppe': '100',
            'fordringstype': '100',
            'fordringsgruppe_id': '13',
            'periodestart': date(2019, 3, 27),
            'periodeslut': date(2019, 3, 28)
        }
        formData.update(dummy_management_form("form"))
        response = self.client.post(self.url, formData)
        root = etree.fromstring(response.content, etree.HTMLParser())
        expected = {
            'fordringsgruppe': 'error.fordringsgruppe_not_found',
            'fordringstype': 'error.fordringstype_not_found'
        }
        expected.update({
            field: 'error.required'
            for field in ['hovedstol', 'forfaldsdato', 'betalingsdato', 'foraeldelsesdato']
        })
        for field, message in expected.items():
            erroritems = root.xpath("//div[@data-field='id_%s']//ul[@class='errorlist']/li" % field)
            self.assertEqual(1, len(erroritems))
            self.assertEqual(message, erroritems[0].attrib.get('data-trans'))
