from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, ProviderViewSet, AvailableSlotViewSet, AppointmentReservationViewSet

router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'providers', ProviderViewSet)
router.register(r'available_slots', AvailableSlotViewSet)
router.register(r'reservations', AppointmentReservationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
