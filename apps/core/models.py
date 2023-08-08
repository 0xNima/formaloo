import os
import hashlib

from functools import partial
from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User
from apps.core.constants import WALLET_UNITS, USD


def upload_to(prefix, _, filename):
    name, ext = os.path.splitext(filename)
    return f'{prefix}/{hashlib.sha1(name.encode()).hexdigest()}{ext}'


class WithDateTime(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class App(WithDateTime):
    title = models.CharField(max_length=256)
    icon = models.URLField(null=True, blank=True)
    description = models.TextField()
    access_link = models.URLField()
    access_key = models.CharField(max_length=128, default=uuid4)
    verified = models.BooleanField(default=False)
    price = models.FloatField(default=0)
    unit = models.SmallIntegerField(choices=WALLET_UNITS, default=USD)

    user = models.ForeignKey(User, related_name='apps', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['id']


class Purchase(WithDateTime):
    app = models.ForeignKey(App, related_name='purchases', on_delete=models.SET_NULL, null=True)
    issued_by = models.ForeignKey(User, related_name='purchases', on_delete=models.SET_NULL, null=True)
    price = models.FloatField()
    unit = models.SmallIntegerField(choices=WALLET_UNITS, default=USD)

    class Meta:
        ordering = ['id']


class Wallet(WithDateTime):
    balance = models.FloatField(default=0)
    unit = models.SmallIntegerField(choices=WALLET_UNITS, default=USD)
    user = models.OneToOneField(User, related_name='wallets', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username or self.user.email or f'user #{self.user.id}'


class UploadedIcon(WithDateTime):
    file = models.ImageField(upload_to=partial(upload_to, 'icons'))
    user = models.ForeignKey(User, related_name='icons', on_delete=models.CASCADE)
