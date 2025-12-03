from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'passenger_name', 'flight_code', 'departure_city', 
                    'arrival_city', 'departure_date', 'price', 'booking_date']
    list_filter = ['departure_date', 'booking_date']
    search_fields = ['passenger_name', 'passport_number', 'flight_code']
    date_hierarchy = 'booking_date'