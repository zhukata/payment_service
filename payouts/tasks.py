from __future__ import annotations

import logging
import time
from typing import Any

from celery import shared_task
from django.db import transaction

from .models import Payout, PayoutStatus

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def process_payout(self: Any, payout_id: int) -> None:
    logger.info("Start processing payout %s", payout_id)
    try:
        with transaction.atomic():
            payout = Payout.objects.select_for_update().get(pk=payout_id)
            if payout.status not in {PayoutStatus.PENDING, PayoutStatus.PROCESSING}:
                logger.info(
                    "Payout %s is already processed with status %s",
                    payout_id,
                    payout.status,
                )
                return

            payout.status = PayoutStatus.PROCESSING
            payout.save(update_fields=["status", "updated_at"])

        # Имитация внешнего вызова / сложной логики
        time.sleep(2)

        with transaction.atomic():
            payout = Payout.objects.select_for_update().get(pk=payout_id)
            payout.status = PayoutStatus.COMPLETED
            payout.save(update_fields=["status", "updated_at"])

        logger.info("Successfully processed payout %s", payout_id)
    except Payout.DoesNotExist:
        logger.error("Payout %s does not exist", payout_id)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Error while processing payout %s", payout_id)
        raise self.retry(exc=exc)
