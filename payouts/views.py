from __future__ import annotations

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Payout
from .serializers import PayoutSerializer, PayoutStatusUpdateSerializer
from .tasks import process_payout


class PayoutViewSet(viewsets.ModelViewSet):
    queryset = Payout.objects.all()
    serializer_class = PayoutSerializer

    def get_serializer_class(self):
        if self.action == "partial_update" and "status" in self.request.data:
            return PayoutStatusUpdateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer: PayoutSerializer) -> None:
        payout = serializer.save()
        # Запуск фоновой задачи обработки
        process_payout.delay(payout.id)

    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):  # type: ignore[override]
        payout = self.get_object()
        process_payout.delay(payout.id)
        return Response({"detail": "Payout processing retriggered."}, status=status.HTTP_202_ACCEPTED)


