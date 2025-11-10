from django.db import models
from django.contrib.auth.models import User

# Each event is created by an organizer (a user)
class Event(models.Model):
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    venue = models.CharField(max_length=200)
    date = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField()  # how many tickets available
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# Discount codes for events
class DiscountCode(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='discount_codes')
    code = models.CharField(max_length=50, unique=True)
    percent_off = models.PositiveIntegerField(default=0)
    valid_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.code} ({self.percent_off}% off)"


# A ticket represents one participant in an event
class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    purchased_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"Ticket for {self.full_name} - {self.event.title}"
