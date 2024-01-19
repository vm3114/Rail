from django.contrib import admin
from .models import *
from django.http import HttpResponseRedirect
from django.urls import reverse

# Register your models here.

class CustomAdminSite(admin.AdminSite):

    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser
    
    def login(self, request):
        login_url = reverse('home')
        return HttpResponseRedirect(login_url)

admin_site = CustomAdminSite(name='customadmin')

admin_site.register(Coach)
admin_site.register(Seat)
admin_site.register(Account)
admin_site.register(JourneySegment)
admin_site.register(DayOfWeek)
admin_site.register(Train)
admin_site.register(Stop)
admin_site.register(Train_stops)
admin_site.register(Booking)
admin_site.register(SeatReservation)