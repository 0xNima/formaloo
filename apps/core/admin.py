from django.contrib import admin
from apps.core.models import App


class AppModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'verified', 'user']
    list_filter = ['verified']
    search_fields = ['title', 'user__username']


admin.site.register(App, AppModelAdmin)

