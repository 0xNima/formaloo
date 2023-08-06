from django.db import transaction
from django.db.models import F
from rest_framework import serializers
from apps.core.models import App, Purchase, UploadedIcon, Wallet
from apps.core.exceptions import InsufficientFundException, SelfPurchaseException


class AppCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = App
        fields = ('title', 'description', 'price', 'user', 'access_link', 'icon')


class AppUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = App
        fields = ('title', 'description', 'price', 'access_link', 'icon')


class AppReadSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    def get_icon(self, obj):
        return obj.icon or None

    def get_created_at(self, obj):
        return int(obj.created_at.timestamp() * 1000)

    class Meta:
        model = App
        fields = ('id', 'title', 'description', 'access_link', 'access_key', 'price', 'created_at', 'icon')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context.get('scope') == 'public':
            data.pop('access_link')
            data.pop('access_key')
        return data


class PurchaseReadSerializer(serializers.ModelSerializer):
    app = AppReadSerializer()
    created_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return int(obj.created_at.timestamp() * 1000)

    class Meta:
        model = Purchase
        fields = ('id', 'app', 'price', 'unit', 'created_at')


class PurchaseWriteSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        app = validated_data['app']
        issuer_by = validated_data['issued_by']

        if app.user_id == issuer_by.id:
            raise SelfPurchaseException()

        with transaction.atomic():
            issuer_wallet = Wallet.objects.select_for_update().filter(
                user=issuer_by.id,
                balance__gte=app.price,
            ).first()

            if issuer_wallet:
                obj = Purchase.objects.create(
                    **validated_data,
                    price=app.price,
                    unit=app.unit
                )

                issuer_wallet.balance -= app.price
                issuer_wallet.save()

                Wallet.objects.filter(user=app.user.id).update(balance=F('balance') + app.price)
            else:
                raise InsufficientFundException()

        return obj

    class Meta:
        model = Purchase
        fields = ('app', 'issued_by')


class UploadedIconSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedIcon
        fields = ('file', 'user')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('user')
        data['url'] = data.pop('file')
        return data
