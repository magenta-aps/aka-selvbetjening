from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(OPENID_CONNECT={'enabled': True})
class MiddlewareTestCase(TestCase):

    def setUp(self) -> None:
        pass

    def test_not_logged_in(self):
        """
        ensure we can't reach the konto view when not logged in
        """
        r = self.client.get(reverse('aka:konto'), follow=False)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, reverse('aka:login') + "?back=" + reverse('aka:konto'))

    def test_not_logged_in_form_view(self):
        """
        ensure we can't do a form post when not logged in, we should get redirected to the login page instead.
        """
        data = {'fordringshaver': 'firstname', 'debitor': 'debitor'}
        r = self.client.post(reverse('aka:inkassosag'), data=data)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, reverse('aka:login') + "?back=" + reverse('aka:inkassosag'))
