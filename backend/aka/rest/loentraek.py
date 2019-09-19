import logging

from aka.forms import LoentraekForm
# When the service is implemented unused imports should be removed,
# but until then they are just commented out as a reference
from django.views.generic import FormView

# from aka.helpers.result import Error, Success
# from aka.helpers.sharedfiles import getSharedJson

logger = logging.getLogger(__name__)


class LoenTraek(FormView):
    '''This class handles the REST interface at /loentraek

    The purpose is to report pay deductions to Prisme.
    '''

    form_class = LoentraekForm
