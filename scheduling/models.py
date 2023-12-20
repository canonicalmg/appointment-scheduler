from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Provider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class AvailableSlot(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        unique_together = ('provider', 'start_time', 'end_time')

class AppointmentReservation(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    slot = models.ForeignKey(AvailableSlot, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)

    def is_expired(self):
        # Check if 30 minutes have passed since the reservation was created
        expiration_time = self.created_at + timedelta(minutes=30)
        return timezone.now() >= expiration_time and not self.confirmed
