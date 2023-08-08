from django.contrib.auth.models import User
from django.test import RequestFactory, override_settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from mixer.backend.django import mixer
from apps.core.models import App
from apps.core.views import AppViewsets
from apps.core.serializers import AppCreateSerializer
from apps.authenticate.tests import WithAuthTestCase


class TestAppViewset(WithAuthTestCase):
    PAGE_SIZE = 5

    def setUp(self) -> None:
        with mixer.ctx(commit=False) as mx:
            user = mx.blend(User, active=True)
            self.tokens = self.get_token({
                'username': user.username,
                'email': user.email,
                'password': user.password,
                'password_confirmation': user.password,
            })

            self.user = User.objects.get(username=user.username)

            self.requester = RequestFactory(headers={
                'Authorization': f'JWT {self.tokens["access"]}'
            })

    @override_settings(PAGE_SIZE=PAGE_SIZE)
    def test_applist(self):
        object_count = 10
        mixer.cycle(count=object_count).blend(App, user=self.user)
        request = self.requester.get('apps/')
        response = AppViewsets.as_view({'get': 'list'})(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data['results']), self.PAGE_SIZE
        )
        self.assertEqual(response.data['count'], object_count)
        self.assertTrue(response.data['next'] is not None)
        self.assertTrue(response.data['previous'] is None)

    def test_create_app(self):
        with mixer.ctx(commit=False) as mx:
            app = mx.blend(App, user=self.user, price=20)
        request = self.requester.post('apps/', data=AppCreateSerializer(app).data, content_type='application/json')
        response = AppViewsets.as_view({'post': 'create'})(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], app.title)
        self.assertEqual(response.data['id'], 1)

    def test_retrieve_app(self):
        app = mixer.blend(App, user=self.user, price=20)
        request = self.requester.get('apps/')
        response = AppViewsets.as_view({'get': 'retrieve'})(request, pk=app.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], app.title)
        self.assertEqual(response.data['access_key'], str(app.access_key))
        self.assertEqual(response.data['id'], 1)

    def test_delete_app(self):
        app = mixer.blend(App, user=self.user, price=20)
        request = self.requester.delete('apps/')
        response = AppViewsets.as_view({'delete': 'destroy'})(request, pk=app.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.assertRaises(ObjectDoesNotExist):
            App.objects.get(pk=app.id)
