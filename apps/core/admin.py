from django.contrib import admin
from apps.core.models import App, Purchase, Wallet, UploadedIcon

admin.site.register(App)
admin.site.register(Purchase)
admin.site.register(Wallet)
admin.site.register(UploadedIcon)
