from __future__ import annotations

from decimal import Decimal
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Payout


class PayoutAPITests(APITestCase):
    def setUp(self) -> None:
        self.list_url = reverse("payout-list")

    @patch("payouts.views.process_payout.delay")
    def test_create_payout_triggers_celery_task(self, mock_delay) -> None:
        data = {
            "amount": "100.50",
            "currency": "usd",
            "recipient_account": "DE1234567890",
            "recipient_name": "John Doe",
            "description": "Test payout",
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        payout = Payout.objects.get()
        self.assertEqual(payout.amount, Decimal("100.50"))
        self.assertEqual(payout.currency, "USD")
        mock_delay.assert_called_once_with(payout.id)

    def test_create_payout_validation_error(self) -> None:
        # отрицательная сумма должна привести к 400
        data = {
            "amount": "-10.00",
            "currency": "USD",
            "recipient_account": "DE1234567890",
            "recipient_name": "John Doe",
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amount", response.data)


