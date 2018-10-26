import datetime


class AKAUtils():
    '''Various utility methods.
    '''

    @staticmethod
    def datefromstringYMD(datestring):
        '''
        Convert a string of the form YYYYMMDD to a datetime object.

        E.g. 20180203 is OK. 2018218 is not OK.

        :param datestring: Date in the form 'YYYYMMDD'.
        :type datestring: String
        :returns: datetime object.
        '''

        return datetime.datetime.strptime(datestring, '%Y%m%d')
