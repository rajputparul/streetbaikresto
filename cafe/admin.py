from django.contrib import admin
from .models import MenuItem,Order,Reservation,Review,Message,NotificationLog
admin.site.register([MenuItem,Order,Reservation,Review,Message,NotificationLog])
