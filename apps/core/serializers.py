from rest_framework import serializers
from apps.core.models import App, Purchase, UploadedIcon


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


class PurchaseSerializer(serializers.ModelSerializer):
    app = AppReadSerializer()
    created_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return int(obj.created_at.timestamp() * 1000)

    class Meta:
        model = Purchase
        fields = ('app', 'issued_at', 'price', 'unit', 'created_at')


class UploadedIconSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedIcon
        fields = ('file', 'user')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('user')
        data['url'] = data.pop('file')
        return data
