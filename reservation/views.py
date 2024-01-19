from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.utils.decorators import method_decorator
from django.db import transaction
from .models import *
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .forms import *
from django.forms import formset_factory, inlineformset_factory
from datetime import datetime
from django.shortcuts import get_object_or_404
from .decorators import *

# Create your views here.


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'You have been successfully logged out.')
        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView):
    template_name = 'login.html'
    success_url = reverse_lazy('home')

    def get_success_url(self):
        messages.success(self.request, 'Login successful.')

        if self.request.user.is_superuser:
            return reverse_lazy('admin:index')
        elif self.request.user.account.is_staff:
            return reverse_lazy('staff')
        else:
            return self.success_url


@superuser_or_staff_required
def staff_page(request):
    trains = Train.objects.all()
    return render(request, 'staff.html', {'trains': trains, 'page': 'Staff Page'})


@superuser_or_staff_required
def add_train(request):
    if request.method == 'POST':
        train_form = TrainForm(request.POST)
        if train_form.is_valid():
            train = train_form.save()
            messages.success(request, 'Train created.')
            return redirect('staff')
    else:
        train_form = TrainForm()

    return render(request, 'add_train.html', {'train_form': train_form})


@superuser_or_staff_required
def delete_train(request, train_id):
    train = Train.objects.get(id = train_id)
    name = f"{train.code}-{train.name}"
    train.delete()
    messages.success(request, f"Train {name} deleted successfully.") 
    return redirect('staff')


@superuser_or_staff_required
def add_stops(request):
    if request.method == 'POST':
        stop_form = StopForm(request.POST)
        if stop_form.is_valid():
            stop = stop_form.save(commit=False)
            stop.save()
            return redirect('add_stops')
    else:
        stop_form = StopForm()

    return render(request, 'add_stops.html', {'stop_form': stop_form})


@superuser_or_staff_required
def add_coach(request, train_id):
    train = Train.objects.get(id = train_id)

    if request.method == 'POST':
        form = CoachForm(request.POST)
        if form.is_valid():
            coach = form.save(commit=False)
            coach.train = train
            coach.save()
            messages.success(request, f'Coach added to {train}')
            return redirect('staff')
    else:
        form = CoachForm()

    return render(request, 'add_coach.html', {'form': form, 'train': train})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            Account.objects.create(user = user, email = request.POST.get('email'))
            auth_login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
        else:
            return render(request, 'signup.html', {'form' : form, 'page': 'TravelRails | Signup'})
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form' : form, 'page': 'TravelRails | Signup'})


def home(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = TrainSearchForm(request.POST)
            if form.is_valid():
                selected_date = form.cleaned_data['selected_date']
                formatted_date = selected_date.strftime('%Y-%m-%d')
                from_stop = form.cleaned_data['from_stop']
                to_stop = form.cleaned_data['to_stop']

                selected_day = datetime.strftime(selected_date, '%a').upper()
                trains_on_day = Train.objects.filter(operating_days__name = selected_day)

                from_stop_qs = Train_stops.objects.filter(stop__station = from_stop, train__in = trains_on_day)
                to_stop_qs = Train_stops.objects.filter(stop__station = to_stop, train__in = trains_on_day)

                common_trains = set(from_stop_qs.values_list('train', flat=True)) & set(to_stop_qs.values_list('train', flat=True))

                valid_trains = []
                for train_id in common_trains:
                    from_order = from_stop_qs.get(train_id = train_id).stop.order
                    to_order = to_stop_qs.get(train_id = train_id).stop.order

                    if from_order < to_order:
                        valid_trains.append(train_id)

                trains = Train.objects.filter(id__in = valid_trains)

                train_details = []
                for train in trains:
                    from_stop_instance = Train_stops.objects.filter(train=train, stop__station=from_stop).first()
                    to_stop_instance = Train_stops.objects.filter(train=train, stop__station=to_stop).first()
                    if from_stop_instance and to_stop_instance:
                        train_details.append({
                            'train': train,
                            'from_stop': from_stop_instance.stop,
                            'to_stop': to_stop_instance.stop,
                            'stop_range' : f"{from_stop_instance.stop.order},{to_stop_instance.stop.order}",
                            'travel_date' : formatted_date
                        })

                return render(request, 'search_results.html', {'form': form, 'train_details': train_details, 'page': 'Search Results'})

        else:
            form = TrainSearchForm()

        return render(request, 'home.html', {'form': form, 'page': 'TravelRails | Home'})
    
    else:
        messages.error(request, 'You need to log in to access this page.')
        return redirect('login')


@login_required(login_url="/login/")
def profile(request):
    user = request.user
    try:
        account = Account.objects.get(user = user)
    except Account.DoesNotExist:
        account = None
    
    account_bookings = Booking.objects.filter(account=account)
    reservations = set()
    seat_reservations = SeatReservation.objects.filter(booking__in=account_bookings)
    for resev in seat_reservations:
        reservations.add(resev)

    return render(request, 'profile.html', {'user': user, 'account': account, 'seat_reservations': reservations, 'page': 'Profile'})

@login_required(login_url="/login/")
def delete_seat_reservation(request, seat_reservation_id):
    seat_reservation = get_object_or_404(SeatReservation, id=seat_reservation_id)
    if request.method == 'POST':
        seat_reservation.delete()
        messages.success(request, 'Booking deleted successfully. You have been refunded.')
    else:
        messages.error(request, 'Invalid request.')
    return redirect('profile')


@login_required(login_url="/login/")
def add_balance(request):
    user = request.user
    try:
        account = Account.objects.get(user=user)
    except Account.DoesNotExist:
        messages.error(request, 'Account not found for the current user.')
        return redirect('profile')
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        try:
            amount = int(amount)
            if amount > 0:
                account.credit += amount
                account.save()
                messages.success(request, f'Successfully added ₹{amount} to your balance.')
            else:
                messages.error(request, 'Please enter a valid positive amount.')
        except ValueError:
            messages.error(request, 'Please enter a valid number for the amount.')

    return redirect('profile')


@login_required(login_url="/login/")
def book_ticket(request, coachCode, trainName, fromStation, toStation, journey_date):
    
    train = Train.objects.get(name=trainName)
    coach = Coach.objects.get(train=train, code=coachCode)
    from_stop = Train_stops.objects.get(train=train, stop__station=fromStation)
    to_stop = Train_stops.objects.get(train=train, stop__station=toStation)
    format = "%Y-%m-%d"
    d = datetime.strptime(journey_date, format).date()
    selected_day = datetime.strftime(d, '%a').upper()

    departure_time = from_stop.stop.time
    arrival_time = to_stop.stop.time
    ticket_price = coach.price_per_segment * (to_stop.stop.order - from_stop.stop.order)
    
    context = {'page': 'Booking',
                    'coachType': coach.coach_type,
                    'coachCode': coachCode,
                    'trainName': trainName,
                    'fromStation': fromStation,
                    'toStation': toStation,
                    'journey_date': journey_date,
                    'departure_time': departure_time,
                    'arrival_time': arrival_time,
                    'ticket_price': ticket_price,
                    'available_seats': get_available_seat(coach, from_stop.stop.order, to_stop.stop.order)}

    if request.method == 'POST':
        num_seats = int(request.POST.get('num_seats'))
        selected_seats = set()
        total_cost = ticket_price * num_seats
        account = Account.objects.get(user = request.user)
       
        if account.credit < total_cost:
            messages.error(request, 'Insufficient Funds!')
            return render(request, 'booking.html', context)
        
        passengers = []
        journey_segments = JourneySegment.objects.filter(
            coach=coach,
            order__gte=from_stop.stop.order,
            order__lt=to_stop.stop.order,
            day = DayOfWeek.objects.get(name = selected_day)
        )
        try:
            with transaction.atomic():
                account.credit -= total_cost
                account.save()
                for i in range(1, num_seats + 1):
                    name = request.POST.get(f'name_{i}')
                    age = request.POST.get(f'age_{i}')
                    seat_number = request.POST.get(f'seat_{i}')
                    bookings = []

                    if seat_number in selected_seats:
                       transaction.set_rollback(True)
                       raise ValueError
                    
                    selected_seats.add(seat_number)
                    
                    seat_reservation = SeatReservation.objects.create(
                    coach = coach,
                    day = DayOfWeek.objects.get(name = selected_day),
                    date = journey_date,
                    name = name,
                    age = age,
                    seat_number = seat_number
                    )

                    for journey_segment in journey_segments:
                        seat = Seat.objects.get(number = seat_number, journey_segment = journey_segment)
                        booking = Booking.objects.create(account = account, seat = seat, price = coach.price_per_segment, seat_reservation = seat_reservation)
                        bookings.append(booking)
                        seat.is_booked = True
                        seat.save()

                    passengers.append({
                        'name': name,
                        'age': age,
                        'seat': seat_number
                    })

        except ValueError:
            messages.error(request, "All passengers must have different seats.")
            return render(request,'booking.html', context)

        messages.success(request, 'Ticket Booked.')
        return render(
            request,
            'confirm_booking.html', {
                'page': 'Your Booking',
                'trainName': trainName,
                'coachCode': coachCode,
                'coachType': coach.coach_type,
                'fromStation': fromStation,
                'toStation': toStation,
                'departure_time': departure_time,
                'arrival_time': arrival_time,
                'numSeats': num_seats,
                'totalCost': total_cost,
                'passengers': passengers,
                'date': journey_date
            }
        )

    return render(request, 'booking.html', context)


def get_available_seat(coach, from_station_order, to_station_order):

    journey_segments = JourneySegment.objects.filter(coach = coach, order__gte = from_station_order, order__lte = to_station_order)
    available_seat_numbers = set()

    for index, journey_segment in enumerate(journey_segments):
        unbooked_seats = Seat.objects.filter(journey_segment=journey_segment, is_booked=False)
        if index == 0:
            available_seat_numbers.update(seat.number for seat in unbooked_seats)
        else:
            booked_seats = Seat.objects.filter(journey_segment=journey_segment, is_booked=True)
            available_seat_numbers.difference_update(seat.number for seat in booked_seats)

    sorted_available_seat_numbers = sorted(available_seat_numbers)
    return sorted_available_seat_numbers