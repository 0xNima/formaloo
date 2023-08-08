from django.contrib.auth.models import User
from django.test import RequestFactory, override_settings
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from rest_framework import status
from mixer.backend.django import mixer
from apps.core.models import App, Purchase, Wallet
from apps.core.views import AppViewsets, VerifiedAppsView, PurchaseViewsets
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

    def test_retrieve_app(self):
        app = mixer.blend(App, user=self.user, price=20)
        request = self.requester.get('apps/')
        response = AppViewsets.as_view({'get': 'retrieve'})(request, pk=app.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], app.title)
        self.assertEqual(response.data['access_key'], str(app.access_key))

    def test_delete_app(self):
        app = mixer.blend(App, user=self.user, price=20)
        request = self.requester.delete('apps/')
        response = AppViewsets.as_view({'delete': 'destroy'})(request, pk=app.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.assertRaises(ObjectDoesNotExist):
            App.objects.get(pk=app.id)


class TestVerifiedApps(WithAuthTestCase):
    def setUp(self) -> None:
        self.target_user = mixer.blend(User, active=True)

        with mixer.ctx(commit=False) as mx:
            this_user = mx.blend(User, active=True)
            self.tokens = self.get_token({
                'username': this_user.username,
                'email': this_user.email,
                'password': this_user.password,
                'password_confirmation': this_user.password,
            })

            self.user = User.objects.get(username=this_user.username)

            self.requester = RequestFactory(headers={
                'Authorization': f'JWT {self.tokens["access"]}'
            })

    def test_verified_applist(self):
        target_user_verified_app_counts = settings.PAGE_SIZE + 1
        target_user_unverified_app_counts = 3
        this_user_verified_app_counts = 3

        mixer.cycle(count=target_user_verified_app_counts).blend(App, user=self.target_user, verified=True)
        mixer.cycle(count=target_user_unverified_app_counts).blend(App, user=self.target_user)
        mixer.cycle(count=this_user_verified_app_counts).blend(App, user=self.user, verified=True)

        request = self.requester.get('apps/verified/')
        response = VerifiedAppsView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data['results']), settings.PAGE_SIZE
        )
        self.assertEqual(response.data['count'], target_user_verified_app_counts)
        self.assertTrue(response.data['next'] is not None)
        self.assertTrue(response.data['previous'] is None)


class TestPurchaseViewset(WithAuthTestCase):
    PAGE_SIZE = 5
    INIT_BALANCE = 100

    def setUp(self) -> None:
        with mixer.ctx(commit=False) as mx:
            user_a = mx.blend(User, active=True)
            user_b = mx.blend(User, active=True)

            self.tokens_a = self.get_token({
                'username': user_a.username,
                'email': user_a.email,
                'password': user_a.password,
                'password_confirmation': user_a.password,
            })

            self.tokens_b = self.get_token({
                'username': user_b.username,
                'email': user_b.email,
                'password': user_b.password,
                'password_confirmation': user_b.password,
            })

            self.user_a = User.objects.get(username=user_a.username)
            self.user_b = User.objects.get(username=user_b.username)

            mixer.blend(Wallet, user=self.user_a, balance=self.INIT_BALANCE)
            mixer.blend(Wallet, user=self.user_b, balance=self.INIT_BALANCE)

            self.requester_a = RequestFactory(headers={
                'Authorization': f'JWT {self.tokens_a["access"]}'
            })

            self.requester_b = RequestFactory(headers={
                'Authorization': f'JWT {self.tokens_b["access"]}'
            })

    @override_settings(PAGE_SIZE=PAGE_SIZE)
    def test_purchase_list(self):
        app = mixer.blend(App, user=self.user_a, price=20)
        purchase_count = 10
        mixer.cycle(count=purchase_count).blend(Purchase, issued_by=self.user_b, app=app)
        request = self.requester_b.get('purchases/')
        response = PurchaseViewsets.as_view({'get': 'list'})(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data['results']), self.PAGE_SIZE
        )
        self.assertEqual(response.data['count'], purchase_count)
        self.assertTrue(response.data['next'] is not None)
        self.assertTrue(response.data['previous'] is None)

    def test_create_purchase(self):
        app_price = 20
        app = mixer.blend(App, user=self.user_a, price=app_price)
        request = self.requester_b.post(
            'purchases/',
            data={
                'app': app.id
            },
            content_type='application/json'
        )
        response = PurchaseViewsets.as_view({'post': 'create'})(request)

        user_a_balance = Wallet.objects.get(user=self.user_a)
        user_b_balance = Wallet.objects.get(user=self.user_b)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(user_a_balance, self.INIT_BALANCE - app_price)
        self.assertTrue(user_b_balance, self.INIT_BALANCE + app_price)
        self.assertTrue(response.data['access_link'] is not None)
        self.assertEqual(response.data['id'], app.id)

    def test_retrieve_purchase(self):
        app_price = 20
        app = mixer.blend(App, user=self.user_a, price=app_price)
        purchase = mixer.blend(Purchase, issued_by=self.user_b, app=app)

        request = self.requester_b.get('purchases/')
        response = PurchaseViewsets.as_view({'get': 'retrieve'})(request, pk=purchase.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], purchase.id)
        self.assertEqual(response.data['app']['id'], app.id)
