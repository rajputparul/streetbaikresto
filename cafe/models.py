from django.db import models
from django.utils import timezone
class MenuItem(models.Model):
 id=models.CharField(max_length=80,primary_key=True); category=models.CharField(max_length=80); name=models.CharField(max_length=160); price=models.DecimalField(max_digits=8,decimal_places=2); image=models.CharField(max_length=160); description=models.TextField(); diet=models.CharField(max_length=20); bestseller=models.BooleanField(default=False); active=models.BooleanField(default=True)
 class Meta: ordering=["category","name"]
 def __str__(self): return self.name
class Order(models.Model):
 STATUSES=[(x,x) for x in ["Order Received","Confirmed","Preparing","Ready","Out for Delivery","Delivered","Cancelled"]]
 public_id=models.CharField(max_length=40,unique=True); customer_name=models.CharField(max_length=120); email=models.EmailField(blank=True); phone=models.CharField(max_length=20); address=models.TextField(blank=True); order_type=models.CharField(max_length=20); table_no=models.CharField(max_length=30,blank=True); instructions=models.TextField(blank=True); latitude=models.FloatField(null=True,blank=True); longitude=models.FloatField(null=True,blank=True); subtotal=models.DecimalField(max_digits=10,decimal_places=2); delivery_charge=models.DecimalField(max_digits=10,decimal_places=2,default=0); tax=models.DecimalField(max_digits=10,decimal_places=2,default=0); total=models.DecimalField(max_digits=10,decimal_places=2); payment_method=models.CharField(max_length=60); payment_status=models.CharField(max_length=30,default="Pending"); status=models.CharField(max_length=30,choices=STATUSES,default="Order Received"); items_json=models.JSONField(default=list); created_at=models.DateTimeField(default=timezone.now); updated_at=models.DateTimeField(auto_now=True)
class Reservation(models.Model):
 STATUSES=[("Pending","Pending"),("Approved","Approved"),("Rejected","Rejected"),("Completed","Completed")]; booking_id=models.CharField(max_length=40,unique=True); name=models.CharField(max_length=120); phone=models.CharField(max_length=20); email=models.EmailField(blank=True); date=models.DateField(); time=models.TimeField(); guests=models.PositiveIntegerField(); request=models.TextField(blank=True); status=models.CharField(max_length=20,choices=STATUSES,default="Pending"); created_at=models.DateTimeField(default=timezone.now)
class Review(models.Model):
 STATUSES=[("Pending","Pending"),("Approved","Approved"),("Rejected","Rejected")]; name=models.CharField(max_length=120); rating=models.PositiveSmallIntegerField(); review=models.TextField(); status=models.CharField(max_length=20,choices=STATUSES,default="Pending"); created_at=models.DateTimeField(default=timezone.now)
class Message(models.Model):
 name=models.CharField(max_length=120); email=models.EmailField(blank=True); phone=models.CharField(max_length=20,blank=True); message=models.TextField(); created_at=models.DateTimeField(default=timezone.now)
class NotificationLog(models.Model):
 order=models.ForeignKey(Order,on_delete=models.CASCADE); channel=models.CharField(max_length=30); event=models.CharField(max_length=60); status=models.CharField(max_length=30); detail=models.TextField(blank=True); created_at=models.DateTimeField(default=timezone.now)
