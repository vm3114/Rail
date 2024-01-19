from django import forms
from .models import *
from django.forms import inlineformset_factory

class TrainSearchForm(forms.Form):
    from_stop = forms.CharField()
    to_stop = forms.CharField()
    selected_date = forms.DateField(label='Select Date', widget=forms.SelectDateWidget)


class BookingForm(forms.Form):
    name = forms.CharField(max_length=255)
    age = forms.IntegerField()


class CoachForm(forms.ModelForm):
    class Meta:
        model = Coach
        fields = ['code', 'coach_type', 'total_seats', 'price_per_segment']
        

class StopForm(forms.ModelForm):
    class Meta:
        model = Stop
        fields = ['station', 'time', 'order']
        widgets = {
            'time': forms.TimeInput(format='%H:%M', attrs={'placeholder': 'HH:MM'}),
        }


class TrainForm(forms.ModelForm):
    class Meta:
        model = Train
        fields = ['code', 'name', 'operating_days', 'stops']

