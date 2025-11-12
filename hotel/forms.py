from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Reservation

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False)
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['table', 'date', 'time', 'guests']

    def clean(self):
        cleaned = super().clean()
        table = cleaned.get('table')
        date = cleaned.get('date')
        time = cleaned.get('time')
        guests = cleaned.get('guests')

        if table and guests and guests > table.capacity:
            raise forms.ValidationError(f"Table {table.number} can seat up to {table.capacity} guests.")

        if table and date and time:
            exists = Reservation.objects.filter(table=table, date=date, time=time, status__in=['Pending', 'Confirmed']).exists()
            if exists:
                raise forms.ValidationError("This table is already booked at the chosen date and time.")
        return cleaned
