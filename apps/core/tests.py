from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status


class WithAuthTestCase(APITestCase):
    register_url = reverse('auth_register')
    login_url = reverse('token_obtain_pair')
    token_refresh = reverse('token_refresh')
    logout_url = reverse('logout')

    def auth_request(self, path, data):
        response = self.client.post(path, data=data)
        body = None

        try:
            body = response.json()
        except TypeError:
            pass

        return response.status_code, body


class TestLoginCase(WithAuthTestCase):

    register_url = reverse('auth_register')
    login_url = reverse('token_obtain_pair')
    token_refresh = reverse('token_refresh')
    logout_url = reverse('logout')

    @classmethod
    def setUpTestData(cls):
        cls.data = {
            "username": "username",
            "password": "Us3rn@me",
            "password_confirmation": "Us3rn@me",
            "email": "username@gmail.com"
        }

    def auth_request(self, path, data):
        response = self.client.post(path, data=data)
        body = None

        try:
            body = response.json()
        except TypeError:
            pass

        return response.status_code, body

    def test_register(self):
        code, body = self.auth_request(self.register_url, self.data)

        self.assertEqual(code, status.HTTP_201_CREATED)
        self.assertEqual(body['username'], self.data['username'])
        self.assertEqual(body['email'], self.data['email'])

    def test_login(self):
        _, body = self.auth_request(self.register_url, self.data)
        code, tokens = self.auth_request(self.login_url, self.data)

        self.assertEqual(code, status.HTTP_200_OK)
        self.assertTrue('access' in tokens)
        self.assertTrue('refresh' in tokens)

    def test_logout(self):
        _, body = self.auth_request(self.register_url, self.data)
        _, tokens = self.auth_request(self.login_url, self.data)

        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {tokens.pop('access')}")

        ok, _ = self.auth_request(self.logout_url, tokens)
        err, _ = self.auth_request(self.logout_url, {'refresh': 'wrong-refresh-token'})
        expired, _ = self.auth_request(self.logout_url, tokens)

        self.assertEqual(ok, status.HTTP_204_NO_CONTENT)
        self.assertEqual(err, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(expired, status.HTTP_400_BAD_REQUEST)
