from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from .models import Table, Reservation
from django.contrib.auth.forms import UserCreationForm
from .forms import ReservationForm

def index(request):
    return render(request, 'index.html')

from django.contrib.auth import logout

def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('index')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff or user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')


@login_required
def home(request):
    tables = Table.objects.all()
    today = timezone.localdate()

    reserved_ids = Reservation.objects.filter(
        date=today,
        status__in=['Pending', 'Confirmed']
    ).values_list('table_id', flat=True)

    for table in tables:
        table.is_reserved_today = table.id in reserved_ids

    user_reservations = Reservation.objects.filter(
        user=request.user
    ).order_by('-date', '-time')

    context = {
        'tables': tables,
        'user_reservations': user_reservations,
    }
    return render(request, 'home.html', context)


@staff_member_required
def admin_dashboard(request):
    tables = Table.objects.all()
    reservations = Reservation.objects.select_related('user', 'table').order_by('-date', '-time')

    if request.method == 'POST' and request.POST.get('action') == 'add_table':
        number = request.POST.get('number')
        capacity = request.POST.get('capacity')
        available = request.POST.get('available') == 'on'

        if Table.objects.filter(number=number).exists():
            messages.error(request, f"Table {number} already exists.")
        else:
            Table.objects.create(number=number, capacity=capacity, is_available=available)
            messages.success(request, f"Table {number} added successfully!")
        return redirect('admin_dashboard')

    if request.method == 'POST' and request.POST.get('action') == 'update_reservation':
        reservation_id = request.POST.get('reservation_id')
        new_status = request.POST.get('status')
        reservation = get_object_or_404(Reservation, id=reservation_id)
        reservation.status = new_status
        reservation.save()
        messages.success(request, f"Reservation #{reservation.id} updated to {new_status}.")
        return redirect('admin_dashboard')

    return render(request, 'admin_dashboard.html', {
        'tables': tables,
        'reservations': reservations
    })

@login_required
def book_table(request):

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.status = 'Pending'
            reservation.save()
            messages.success(request, f"Table {reservation.table.number} booked successfully for {reservation.date} at {reservation.time}!")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ReservationForm()

    return render(request, 'book_table.html', {'form': form})


@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if reservation.status in ['Pending', 'Confirmed']:
        reservation.status = 'Cancelled'
        reservation.save()
        messages.success(request, f"Reservation for Table {reservation.table.number} on {reservation.date} has been cancelled.")
    else:
        messages.info(request, "This reservation cannot be cancelled.")

    return redirect('home')
