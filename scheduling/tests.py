from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Client, Provider, AvailableSlot, AppointmentReservation
from django.contrib.auth.models import User
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from django.utils import timezone

class AvailableSlotViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.provider_user = User.objects.create_user(username='provider', password='test')
        self.provider = Provider.objects.create(user=self.provider_user)

        self.client_user = User.objects.create_user(username='client', password='test')
        self.client_obj = Client.objects.create(user=self.client_user)

    
    def test_create_slots(self):
        url = reverse('availableslot-list') 
        data = {
            'provider': self.provider.id,
            'start_time': '2023-01-01T08:00:00',
            'end_time': '2023-01-01T10:00:00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AvailableSlot.objects.count(), 8)  # 8 slots of 15 minutes each

    def test_get_available_slots(self):
        start_time = datetime.now() + timedelta(hours=25)
        end_time = start_time + timedelta(hours=7)
        reserved_slot_time = start_time + timedelta(hours=3)

        # Create available slots
        while start_time < end_time:
            AvailableSlot.objects.create(provider=self.provider, start_time=start_time, end_time=start_time + timedelta(minutes=15))
            start_time += timedelta(minutes=15)

        # Reserve one slot
        reserved_slot = AvailableSlot.objects.get(start_time=reserved_slot_time)
        AppointmentReservation.objects.create(slot=reserved_slot, client=self.client_obj, confirmed=True)

        url = reverse('availableslot-list') + '?provider=' + str(self.provider.id)
        response = self.client.get(url)
        
        # Count the number of available slots excluding the reserved one
        available_slots = response.data 
        self.assertEqual(len(available_slots), 27)  # 28 slots in total, 1 is reserved


    def test_get_available_slots_expired_confirmation(self):
        start_time = datetime.now() + timedelta(hours=25)
        end_time = start_time + timedelta(hours=7)
        reserved_slot_time = start_time + timedelta(hours=3)

        # Create available slots
        while start_time < end_time:
            AvailableSlot.objects.create(provider=self.provider, start_time=start_time, end_time=start_time + timedelta(minutes=15))
            start_time += timedelta(minutes=15)

        # Reserve one slot
        reserved_slot = AvailableSlot.objects.get(start_time=reserved_slot_time)
        reservation = AppointmentReservation.objects.create(slot=reserved_slot, client=self.client_obj)

        # Manually set created_at to more than 30 minutes ago and save
        reservation.created_at = timezone.now() - timedelta(minutes=31)
        reservation.save()

        url = reverse('availableslot-list') + '?provider=' + str(self.provider.id)
        response = self.client.get(url)

        # Count the number of available slots including the expired one
        available_slots = response.data
        self.assertEqual(len(available_slots), 28)  # All slots should be available
        

class AppointmentReservationViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client_user = User.objects.create_user(username='client', password='test')
        self.client_obj = Client.objects.create(user=self.client_user)
        self.provider_user = User.objects.create_user(username='provider', password='test')
        self.provider = Provider.objects.create(user=self.provider_user)

    def test_create_reservation(self):
        url = reverse('appointmentreservation-list')
        start_time = timezone.now() + timedelta(hours=48)
        slot = AvailableSlot.objects.create(provider=self.provider, start_time=start_time, end_time = start_time + timedelta(hours=2))
        data = {
            'client': self.client_obj.id,
            'slot': slot.id
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AppointmentReservation.objects.count(), 1)

    def test_create_reservation_fails_24hr(self):
        url = reverse('appointmentreservation-list')
        start_time = timezone.now()
        # create a slot that is not 24 hours in advance
        slot = AvailableSlot.objects.create(provider=self.provider, start_time=start_time, end_time = start_time + timedelta(hours=2))
        data = {
            'client': self.client_obj.id,
            'slot': slot.id
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(AppointmentReservation.objects.count(), 0)
