from django.db import models

class Booking(models.Model):
    flight_code = models.CharField(max_length=10)
    departure_city = models.CharField(max_length=100)
    arrival_city = models.CharField(max_length=100)
    departure_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    passenger_name = models.CharField(max_length=200)
    passport_number = models.CharField(max_length=50)
    

    booking_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.passenger_name} - {self.flight_code}"