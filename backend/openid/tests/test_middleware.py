from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(OPENID_CONNECT={'enabled': True})
class MiddlewareTestCase(TestCase):
    def setUp(self) -> None:
        pass

    def test_not_logged_in(self):
        """
        ensure we cant reach the vu js app when not logged in
        """
        r = self.client.get(reverse('index'), follow=False)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, reverse('openid:login'))

    def test_not_logged_in_form_view(self):
        """
        ensure we cant do a form post when not logged in, we should get redirected to the login page instead.
        """
        data = {'fordringshaver': 'firstname', 'debitor': 'debitor'}
        r = self.client.post(reverse('inkassosag'), data=data)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, reverse('openid:login'))
