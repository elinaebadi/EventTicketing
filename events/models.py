from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from django.db.models import Count


class EventManager(models.Manager):
    def upcoming(self):
        return self.filter(date__gte=timezone.now())

    def with_remaining_capacity(self):
        return self.annotate(
            sold=Count('tickets')
        ).filter(capacity__gt=models.F('sold'))


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

    objects = EventManager()

    def apply_discount(self, code=None):
        final_price = self.price
        discount_percent = 0

        if code:
            try:
                discount = self.discount_codes.get(code=code)
                if not discount.is_valid():
                    return final_price, discount_percent, "Discount code expired or max uses reached."

                discount_percent = discount.percent_off
                final_price = self.price - (self.price * Decimal(discount_percent) / 100)

            except DiscountCode.DoesNotExist:
                return final_price, discount_percent, "Invalid discount code."

        return final_price, discount_percent, None

    def __str__(self):
        return self.title

    @property
    def remaining_capacity(self):
        return self.capacity - self.tickets.count()


# Discount codes for events
class DiscountCode(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='discount_codes')
    code = models.CharField(max_length=50, unique=True)
    percent_off = models.PositiveIntegerField(default=0)
    valid_until = models.DateTimeField(null=True, blank=True)
    max_uses = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.code} ({self.percent_off}% off)"

    @property
    def uses_count(self):
        return Ticket.objects.filter(event=self.event, discount_code=self.code).count()

    def is_valid(self):
        if self.valid_until and self.valid_until < timezone.now():
            return False
        if self.max_uses > 0 and self.uses_count >= self.max_uses:
            return False
        return True


# A ticket represents one participant in an event
class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    purchased_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    discount_code = models.CharField(max_length=50, blank=True, null=True)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Ticket for {self.full_name} - {self.event.title}"


