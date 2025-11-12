from django.contrib import admin
from .models import Table, Reservation

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'capacity', 'is_available')
    list_editable = ('is_available',)
    ordering = ('number',)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'table', 'date', 'time', 'guests', 'status')
    list_filter = ('status', 'date')
    search_fields = ('user__username', 'table__number')
