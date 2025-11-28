from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'venue', 'date', 'price', 'capacity']

class TicketPurchaseForm(forms.Form):
    full_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    discount_code = forms.CharField(
        max_length=50,
        required=False,
        label="Discount Code (Optional)"
    )

class DiscountApplyForm(forms.Form):
    code = forms.CharField(max_length=50, label="Discount Code")