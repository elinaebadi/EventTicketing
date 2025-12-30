from django import forms
from .models import Event, DiscountCode
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'venue', 'date', 'price', 'capacity']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

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

class DiscountCodeForm(forms.ModelForm):
    class Meta:
        model = DiscountCode
        fields = ['code', 'percent_off', 'valid_until', 'max_uses']
        widgets = {
            'valid_until': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')