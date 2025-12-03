from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers

from .models import Payout, PayoutStatus


class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = [
            "id",
            "amount",
            "currency",
            "recipient_account",
            "recipient_name",
            "status",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_amount(self, value: Decimal) -> Decimal:
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value

    def validate_currency(self, value: str) -> str:
        if len(value) != 3 or not value.isalpha():
            raise serializers.ValidationError("Currency must be a 3-letter code (e.g. USD).")
        return value.upper()

    def validate(self, attrs: dict) -> dict:
        # Можно добавить дополнительные бизнес-правила здесь
        return super().validate(attrs)


class PayoutStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = ["status"]

    def validate_status(self, value: str) -> str:
        if value not in PayoutStatus.values:
            raise serializers.ValidationError("Unsupported status.")
        return value


