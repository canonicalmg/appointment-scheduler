from rest_framework import serializers
from .models import Client, Provider, AvailableSlot, AppointmentReservation

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = '__all__'

class AvailableSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableSlot
        fields = '__all__'

class AppointmentReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentReservation
        fields = '__all__'
