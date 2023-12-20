from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Client, Provider, AvailableSlot, AppointmentReservation
from .serializers import (ClientSerializer, ProviderSerializer,
                          AvailableSlotSerializer, AppointmentReservationSerializer)
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.utils import timezone
from django.db.models import Q
from dateutil.parser import parse

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer


class AvailableSlotViewSet(viewsets.ModelViewSet):
    queryset = AvailableSlot.objects.all()
    serializer_class = AvailableSlotSerializer

    def get_queryset(self):
        queryset = AvailableSlot.objects.all()
        provider_id = self.request.query_params.get('provider')
        date = self.request.query_params.get('date')

        if provider_id is not None:
            queryset = queryset.filter(provider_id=provider_id)

        if date:
            date = datetime.strptime(date, '%Y-%m-%d')
        else:
            date = datetime.now() + timedelta(days=1)

        start_date = make_aware(date)
        end_date = start_date + timedelta(days=7)

        # Exclude slots that have a confirmed reservation or a non-expired reservation awaiting confirmation
        reservation_conditions = Q(
            # Confirmed reservations
            confirmed=True
        ) | Q(
            # Unexpired unconfirmed reservations
            created_at__gte=timezone.now() - timedelta(minutes=30),
            confirmed=False
        )

        reserved_slots = AppointmentReservation.objects.filter(
            reservation_conditions,
            slot__provider_id=provider_id,
        ).values_list('slot', flat=True)
        return queryset.filter(start_time__range=(start_date, end_date)).exclude(id__in=reserved_slots)
    
    def create(self, request, *args, **kwargs):
        provider_id = request.data.get('provider')
        start_time = parse(request.data.get('start_time'))
        end_time = parse(request.data.get('end_time'))

        if not provider_id or not start_time or not end_time:
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        if start_time >= end_time:
            return Response({"error": "End time must be after start time."}, status=status.HTTP_400_BAD_REQUEST)

        interval = timedelta(minutes=15)
        slots = []

        while start_time < end_time:
            slot_end_time = start_time + interval
            if slot_end_time > end_time:
                break
            # Round down start_time to the nearest 15 minutes to avoid overlapping
            start_time = start_time.replace(minute=(start_time.minute // 15) * 15, second=0, microsecond=0)

            # Check if the slot already exists
            if not AvailableSlot.objects.filter(
                provider_id=provider_id, 
                start_time=start_time, 
                end_time=slot_end_time
            ).exists():
                slots.append(AvailableSlot(provider_id=provider_id, start_time=start_time, end_time=slot_end_time))

            start_time += interval

        AvailableSlot.objects.bulk_create(slots)
        return Response({"status": "Slots created successfully"}, status=status.HTTP_201_CREATED)


class AppointmentReservationViewSet(viewsets.ModelViewSet):
    queryset = AppointmentReservation.objects.all()
    serializer_class = AppointmentReservationSerializer

    def create(self, request, *args, **kwargs):
        slot_id = request.data.get('slot')

        # Validate the slot
        try:
            slot = AvailableSlot.objects.get(id=slot_id)
        except AvailableSlot.DoesNotExist:
            return Response({'error': 'Slot not found'}, status=status.HTTP_404_NOT_FOUND)
        # Check if the slot is already reserved and not expired
        if AppointmentReservation.objects.filter(
            slot=slot, 
            created_at__gte=timezone.now() - timedelta(minutes=30),
            confirmed=False
        ).exists():
            return Response({'error': 'Slot already reserved'}, status=status.HTTP_400_BAD_REQUEST)
        # Check if the reservation is at least 24 hours in advance
        if slot.start_time < timezone.now() + timedelta(hours=24):
            return Response({'error': 'Reservations must be made at least 24 hours in advance'}, status=status.HTTP_400_BAD_REQUEST)

        # Proceed with normal creation
        return super().create(request, *args, **kwargs)

    @action(methods=['post'], detail=True, url_path='confirm', url_name='confirm_reservation')
    def confirm_reservation(self, request, pk=None):
        reservation = self.get_object()
        if reservation.confirmed:
            return Response({'status': 'reservation already confirmed'})
        print(1)
        if reservation.is_expired():
            return Response({'error': 'Reservation expired'}, status=status.HTTP_400_BAD_REQUEST)
        print(2)
        reservation.confirmed = True
        reservation.save()
        print(3)
        return Response({'status': 'reservation confirmed'})

