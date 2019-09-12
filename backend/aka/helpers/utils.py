import datetime
import base64


class AKAUtils():
    '''Various utility methods.
    '''

    @staticmethod
    def datefromstring(datestring):
        '''
        Convert a string of the form YYYY-MM-DD to a datetime object.

        E.g. 20180203 is OK. 2018218 is not OK.

        :param datestring: Date in the form 'YYYY-MM-DD'.
        :type datestring: String
        :returns: datetime object.
        '''

        return datetime.datetime.strptime(datestring, '%Y-%m-%d')

    @staticmethod
    def datetostring(date):
        '''
        Convert a date object to a string of the form YYYY-MM-DD.

        E.g. 20180203 is OK. 2018218 is not OK.

        :param datestring: Date in the form 'YYYY-MM-DD'.
        :type datestring: String
        :returns: datetime object.
        '''

        return datetime.datetime.strftime(date, '%Y-%m-%d')

    @staticmethod
    def get_file_contents_base64(file):
        with file.open('rb') as fp:
            data = fp.read()
            return base64.b64encode(data).decode("ascii")
