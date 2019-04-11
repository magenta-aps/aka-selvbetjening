import requests
from aka.helpers.result import Success  # , Error


class Prisme():
    '''Class that handles communication with the Prisme system.
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
