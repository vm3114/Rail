from django import template
from reservation.models import *

register = template.Library()

@register.filter(name = 'coach_has_available_seats')
def coach_has_available_seats(coach, orders):
    orders = orders.split(',')
    journey_segments = JourneySegment.objects.filter(coach = coach, order__gte = orders[0], order__lte = orders[1])
    available_seat_numbers = set()

    for index, journey_segment in enumerate(journey_segments):
        unbooked_seats = Seat.objects.filter(journey_segment=journey_segment, is_booked=False)
        if index == 0:
            available_seat_numbers.update(seat.number for seat in unbooked_seats)
        else:
            booked_seats = Seat.objects.filter(journey_segment=journey_segment, is_booked=True)
            available_seat_numbers.difference_update(seat.number for seat in booked_seats)

    if len(available_seat_numbers) > 0:
        return True
    
    else:
        return False

@register.simple_tag
def calculate_price(coach, to_stop, from_stop):
    return coach.price_per_segment * (to_stop.order - from_stop.order)

@register.filter(name = 'train_total_seats')
def train_total_seats(train):
    sum = 0
    for coach in Coach.objects.filter(train = train):
        sum += coach.total_seats
    return sum