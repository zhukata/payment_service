from __future__ import annotations

from django.contrib import admin

from .models import Payout


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ("id", "amount", "currency", "recipient_account", "status", "created_at")
    list_filter = ("status", "currency", "created_at")
    search_fields = ("recipient_account", "recipient_name", "description")


