from django.shortcuts import render, redirect, get_object_or_404
from .models import Event, Ticket, DiscountCode
from .forms import EventForm, TicketPurchaseForm, DiscountApplyForm
from django.utils import timezone

def event_list(request):
    events = Event.objects.all().order_by('date')  # fetch events from DB
    return render(request, 'events/event_list.html', {'events': events})

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Check if the user is the organizer
    is_organizer = request.user.is_authenticated and (request.user == event.organizer)

    discount_codes = event.discount_codes.all() if is_organizer else None
    tickets = event.tickets.all() if is_organizer else None

    return render(request, 'events/event_detail.html', {
        'event': event,
        'is_organizer': is_organizer,
        'discount_codes': discount_codes,
        'tickets': tickets,
    })

def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user  # organizer = logged-in user
            event.save()
            return redirect('event_list')
    else:
        form = EventForm()

    return render(request, 'events/create_event.html', {'form': form})

def apply_discount(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    final_price = event.price
    discount_applied = None
    error = None

    if request.method == "POST":
        form = DiscountApplyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]

            try:
                discount = DiscountCode.objects.get(code=code, event=event)

                # check expiration
                if discount.valid_until and discount.valid_until < timezone.now():
                    error = "This discount code has expired."

                else:
                    discount_applied = discount.percent_off
                    final_price = event.price - (event.price * discount.percent_off / 100)

            except DiscountCode.DoesNotExist:
                error = "Invalid discount code."

    else:
        form = DiscountApplyForm()

    return render(request, "events/apply_discount.html", {
        "event": event,
        "form": form,
        "error": error,
        "discount": discount_applied,
        "final_price": final_price,
    })

def buy_ticket(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if event.tickets.count() >= event.capacity:
        return render(request, 'events/buy_ticket.html', {
            'event': event,
            'error': 'This event is fully booked.'
        })

    final_price = event.price
    discount_applied = 0

    if request.method == 'POST':
        form = TicketPurchaseForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            email = form.cleaned_data['email']
            code = form.cleaned_data.get('discount_code')

            # Apply discount if present
            if code:
                try:
                    discount = DiscountCode.objects.get(code=code, event=event)
                    if discount.valid_until and discount.valid_until < timezone.now():
                        error = "Discount code expired."
                        return render(request, 'events/buy_ticket.html', {
                            'event': event,
                            'form': form,
                            'error': error
                        })

                    discount_applied = discount.percent_off
                    final_price = event.price - (event.price * discount.percent_off / 100)

                except DiscountCode.DoesNotExist:
                    return render(request, 'events/buy_ticket.html', {
                        'event': event,
                        'form': form,
                        'error': "Invalid discount code."
                    })

            # Create ticket with final price & discount code
            Ticket.objects.create(
                event=event,
                buyer=request.user,
                full_name=full_name,
                email=email,
                discount_code=code,
                final_price=final_price
            )

            return redirect('event_detail', event_id=event.id)

    else:
        form = TicketPurchaseForm()

    return render(request, 'events/buy_ticket.html', {
        'event': event,
        'form': form,
        'final_price': final_price,
        'discount': discount_applied
    })