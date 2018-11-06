import requests
from akasite.rest.utils import AKAUtils


class Prisme():
    '''Class tohandle communication with Prisme system.
    '''

    def __init__(self):
        pass

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

    def getRentenota(self, fromdate, todate):
        '''Given a period, will fetch the corresponding rentenote
        from Prisme.

        :param fromdate: Start date of the period.
        :type fromdate: string conforming to this date pattern: YYYYMMDD.
        :param todate: End date of the period.
        :type todate: string conforming to this date pattern: YYYYMMDD.
        :returns: rentenota data as a JSON structure.
        '''

        post1 = {'dato': AKAUtils.datetostring(fromdate),
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
        post2 = {'dato': AKAUtils.datetostring(todate),
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

        return res
