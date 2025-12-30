from django.shortcuts import render, redirect, get_object_or_404
from .models import Event, Ticket
from .forms import EventForm, TicketPurchaseForm, DiscountCodeForm, SignUpForm
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.contrib.auth import login
import logging

logger = logging.getLogger(__name__)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            logger.info(f"New user registered: {user.username}")

            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('event_list')
    else:
        logger.warning("Signup failed: invalid form data")

        form = SignUpForm()
    return render(request, 'events/signup.html', {'form': form})

def event_list(request):
    events = Event.objects.all().order_by('date')  # fetch events from DB
    return render(request, 'events/event_list.html', {'events': events})

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    is_organizer = request.user.is_authenticated and (request.user == event.organizer)
    discount_codes = event.discount_codes.all() if is_organizer else None
    tickets = event.tickets.all() if is_organizer else None

    user_ticket = None
    if request.user.is_authenticated:
        user_ticket = event.tickets.filter(buyer=request.user).first()

    logger.info(
        f"Event viewed | Event: {event.title} | "
        f"User: {request.user if request.user.is_authenticated else 'Anonymous'}"
    )

    return render(request, 'events/event_detail.html', {
        'event': event,
        'is_organizer': is_organizer,
        'discount_codes': discount_codes,
        'tickets': tickets,
        'user_ticket': user_ticket,
    })

@login_required
def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()

            logger.info(
                f"Event created | Organizer: {request.user.username} | "
                f"Event: {event.title}"
            )

            messages.success(request, "Event created successfully!")
            return redirect('event_list')
    else:
        form = EventForm()

    return render(request, 'events/create_event.html', {'form': form})

@login_required
def create_discount(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.user != event.organizer:
        logger.warning(
            f"Unauthorized discount creation attempt | "
            f"User: {request.user.username} | Event: {event.title}"
        )

        messages.error(request, "You are not allowed to create discounts for this event.")
        return redirect('event_detail', event_id=event.id)

    if request.method == "POST":
        form = DiscountCodeForm(request.POST)
        if form.is_valid():
            discount = form.save(commit=False)
            discount.event = event
            discount.save()

            logger.info(
                f"Discount created | Event: {event.title} | "
                f"Code: {discount.code} | By: {request.user.username}"
            )

            messages.success(request, f"Discount code '{discount.code}' created!")
            return redirect('event_detail', event_id=event.id)
    else:
        form = DiscountCodeForm()

    return render(request, 'events/create_discount.html', {'form': form, 'event': event})

@login_required
def buy_ticket(request, event_id):
    with transaction.atomic():
        event = Event.objects.select_for_update().get(id=event_id)

        if event.remaining_capacity <= 0:
            logger.error(f"Ticket purchase failed (full) | Event: {event.title}")

            return render(request, 'events/buy_ticket.html', {
                'event': event,
                'error': 'This event is fully booked.'
            })

        final_price = event.price
        discount_applied = 0

        if request.method == 'POST':
            form = TicketPurchaseForm(request.POST)
            if form.is_valid():
                code = form.cleaned_data.get('discount_code')
                final_price, discount_applied, error = event.apply_discount(code)

                if error:
                    logger.warning(
                        f"Invalid discount | Event: {event.title} | "
                        f"Code: {code} | User: {request.user.username}"
                    )

                    return render(request, 'events/buy_ticket.html', {
                        'event': event,
                        'form': form,
                        'error': error
                    })

                # Create ticket with final price & discount code
                Ticket.objects.create(
                    event=event,
                    buyer=request.user,
                    full_name=form.cleaned_data['full_name'],
                    email=form.cleaned_data['email'],
                    discount_code=code,
                    final_price=final_price
                )

                logger.info(
                    f"Ticket purchased | User: {request.user.username} | "
                    f"Event: {event.title} | Price: {final_price}"
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