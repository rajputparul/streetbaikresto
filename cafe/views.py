import json,math,os,secrets,base64,urllib.request,urllib.parse
from django.conf import settings
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Sum,Count
from django.http import JsonResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import MenuItem,Order,Reservation,Review,Message,NotificationLog

def home(request): return render(request,"index.html",{"categories":categories()})
def customer_login(request):
 if request.user.is_authenticated and not request.user.is_staff: return redirect("home")
 if request.method=="POST":
  email=request.POST.get("email","").strip().lower(); password=request.POST.get("password","")
  user=User.objects.filter(email__iexact=email,is_staff=False).first()
  if user and user.check_password(password): login(request,user); return redirect("home")
  return render(request,"auth.html",{"mode":"login","error":"We couldn't match that email and password."})
 return render(request,"auth.html",{"mode":"login"})
def customer_register(request):
 if request.user.is_authenticated and not request.user.is_staff: return redirect("home")
 if request.method=="POST":
  name=request.POST.get("name","").strip(); email=request.POST.get("email","").strip().lower(); password=request.POST.get("password","")
  if not name or not email or len(password)<8: return render(request,"auth.html",{"mode":"register","error":"Add your name, a valid email and a password of at least 8 characters."})
  if User.objects.filter(email__iexact=email).exists(): return render(request,"auth.html",{"mode":"register","error":"An account already exists for that email."})
  user=User.objects.create_user(username=email,email=email,password=password,first_name=name)
  login(request,user); return redirect("home")
 return render(request,"auth.html",{"mode":"register"})
def customer_logout(request): logout(request); return redirect("home")
def track(request): return render(request,"track.html")
def categories():
 return [{"name":n,"image":i,"icon":x} for n,i,x in [("All","all","🍽️"),("Burgers","burger-category.jpg","🍔"),("Chef Special","chicken-category.jpg","👨‍🍳"),("Combos","burger-category.jpg","🍱"),("Hot & Crispy","chicken-category.jpg","🍗"),("Drinks","drinks-category.jpg","🥤"),("Frappes","drinks-category.jpg","☕"),("Shakes","drinks-category.jpg","🥤")]]
def api_menu(request): return JsonResponse({"items":list(MenuItem.objects.filter(active=True).values()),"categories":categories()})
def new_id(prefix="SB"):
 while True:
  x=f"{prefix}-{__import__('datetime').datetime.now().strftime('%Y%m%d')}-{secrets.randbelow(9000)+1000}"
  if not Order.objects.filter(public_id=x).exists(): return x
def send_whatsapp(order,event):
 msg=f"🔔 Street Baik - {'NEW ORDER' if event=='order_created' else 'ORDER UPDATE'}\nOrder: {order.public_id}\nCustomer: {order.customer_name}\nPhone: {order.phone}\nType: {order.order_type}\nTotal: ₹{order.total:.0f}\nStatus: {order.status}\nTrack: {request_host(order)}"
 sid,token,frm,to=settings.TWILIO_ACCOUNT_SID,settings.TWILIO_AUTH_TOKEN,settings.TWILIO_WHATSAPP_FROM,settings.CLIENT_WHATSAPP
 if not all([sid,token,frm,to]): NotificationLog.objects.create(order=order,channel="WhatsApp",event=event,status="Not configured",detail="Add Twilio WhatsApp credentials and CLIENT_WHATSAPP to .env"); return False
 try:
  data=urllib.parse.urlencode({"To":"whatsapp:+91"+to.replace("+91","").replace(" ",""),"From":"whatsapp:"+frm.replace("whatsapp:",""),"Body":msg}).encode(); auth=base64.b64encode(f"{sid}:{token}".encode()).decode(); req=urllib.request.Request(f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",data=data,headers={"Authorization":"Basic "+auth}); urllib.request.urlopen(req,timeout=10).read(); NotificationLog.objects.create(order=order,channel="WhatsApp",event=event,status="Sent"); return True
 except Exception as e: NotificationLog.objects.create(order=order,channel="WhatsApp",event=event,status="Failed",detail=str(e)[:500]); return False
def request_host(order): return "Configure your public domain in production"
@csrf_exempt
@require_POST
@csrf_exempt
@require_POST
def create_order(request):
 try: p=json.loads(request.body)
 except: return JsonResponse({"ok":False,"error":"Invalid request."},status=400)
 required=["name","phone","order_type","items","payment_method"]
 if any(not p.get(x) for x in required): return JsonResponse({"ok":False,"error":"Please fill all required order details."},status=400)
 phone=str(p["phone"]).strip()
 if not phone.isdigit() or len(phone)!=10:return JsonResponse({"ok":False,"error":"Phone number must contain exactly 10 digits."},status=400)
 if p["order_type"] not in ["Takeaway","Dine-in"]: return JsonResponse({"ok":False,"error":"Please choose Takeaway or Dine-in."},status=400)
 clean=[]; subtotal=0
 for r in p["items"]:
  item=MenuItem.objects.filter(pk=str(r.get("id")),active=True).first(); qty=int(r.get("quantity",0))
  if not item or qty<1 or qty>99:return JsonResponse({"ok":False,"error":"Invalid cart item."},status=400)
  line=float(item.price)*qty; subtotal+=line; clean.append({"id":item.id,"name":item.name,"price":float(item.price),"quantity":qty,"line_total":line})
 order=Order.objects.create(public_id=new_id(),customer_name=p["name"].strip(),email=p.get("email","").strip(),phone=phone,address="",order_type=p["order_type"],table_no=str(p.get("table_no","")).strip(),instructions=str(p.get("instructions","")).strip(),latitude=None,longitude=None,subtotal=subtotal,total=subtotal,payment_method=p["payment_method"],items_json=clean)
 send_whatsapp(order,"order_created")
 return JsonResponse({"ok":True,"public_id":order.public_id,"total":float(order.total),"status":order.status})
def get_order(request,public_id):
 o=get_object_or_404(Order,public_id=public_id.upper()); data={"public_id":o.public_id,"customer_name":o.customer_name,"order_type":o.order_type,"total":float(o.total),"status":o.status,"items":o.items_json,"updated_at":o.updated_at.strftime("%Y-%m-%d %H:%M:%S")}; return JsonResponse({"ok":True,"order":data,"statuses":[x[0] for x in Order.STATUSES]})
@csrf_exempt
@require_POST
def create_reservation(request):
 try:p=json.loads(request.body)
 except:return JsonResponse({"ok":False,"error":"Invalid request."},status=400)
 if not all(p.get(x) for x in ["name","phone","date","time","guests"]):return JsonResponse({"ok":False,"error":"Please fill all required reservation fields."},status=400)
 phone=str(p["phone"]).strip()
 if not phone.isdigit() or len(phone)!=10:return JsonResponse({"ok":False,"error":"Phone number must contain exactly 10 digits."},status=400)
 r=Reservation.objects.create(booking_id=new_id("TB"),name=p["name"].strip(),phone=phone,email=p.get("email","").strip(),date=p["date"],time=p["time"],guests=int(p["guests"]),request=p.get("request","").strip()); return JsonResponse({"ok":True,"booking_id":r.booking_id,"status":r.status})
@csrf_exempt
@require_POST
def create_review(request):
 try:p=json.loads(request.body); rating=int(p.get("rating",0))
 except:return JsonResponse({"ok":False,"error":"Invalid review."},status=400)
 if not p.get("name") or rating not in range(1,6) or not p.get("review"):return JsonResponse({"ok":False,"error":"Please provide name, rating and review."},status=400)
 Review.objects.create(name=p["name"].strip(),rating=rating,review=p["review"].strip()); return JsonResponse({"ok":True})
@csrf_exempt
@require_POST
def create_message(request):
 try:p=json.loads(request.body)
 except:return JsonResponse({"ok":False,"error":"Invalid request."},status=400)
 if not p.get("name") or not p.get("message"):return JsonResponse({"ok":False,"error":"Name and message are required."},status=400)
 Message.objects.create(name=p["name"].strip(),email=p.get("email","").strip(),phone=p.get("phone","").strip(),message=p["message"].strip()); return JsonResponse({"ok":True})
def staff_login(request):
 if request.user.is_authenticated: return staff_dashboard(request)
 if request.method=="POST":
  u=authenticate(request,username=request.POST.get("username"),password=request.POST.get("password"))
  if u and u.is_staff: login(request,u); return redirect("staff")
  return render(request,"admin.html",{"error":"Invalid username or password."})
 return render(request,"admin.html",{"error":None})
def staff_logout(request): logout(request); return redirect("staff")
@login_required
def staff_dashboard(request):
 if not request.user.is_staff: return redirect("home")
 orders=Order.objects.all().order_by("-created_at"); reservations=Reservation.objects.all().order_by("-created_at"); reviews=Review.objects.all().order_by("-created_at"); messages=Message.objects.all().order_by("-created_at"); stats={"orders":orders.count(),"pending":orders.filter(status="Pending").count(),"revenue":orders.filter(status__in=["Confirmed","Preparing","Ready","Completed"]).aggregate(x=Sum("total"))["x"] or 0,"reservations":reservations.count(),"reviews":reviews.count(),"messages":messages.count()}; return render(request,"admin.html",{"logged_in":True,"orders":orders,"reservations":reservations,"reviews":reviews,"messages":messages,"stats":stats,"statuses":[x[0] for x in Order.STATUSES]})
@login_required
@csrf_exempt
@require_POST
def update_order_status(request,order_id):
 try:p=json.loads(request.body)
 except:return JsonResponse({"ok":False,"error":"Invalid request."},status=400)
 status=p.get("status"); order=get_object_or_404(Order,pk=order_id)
 if status not in dict(Order.STATUSES):return JsonResponse({"ok":False,"error":"Invalid status."},status=400)
 order.status=status;order.save();send_whatsapp(order,"status_"+status.lower());return JsonResponse({"ok":True,"status":status})
@login_required
@csrf_exempt
@require_POST
def update_reservation_status(request,item_id):
 try:p=json.loads(request.body)
 except:return JsonResponse({"ok":False,"error":"Invalid request."},status=400)
 r=get_object_or_404(Reservation,pk=item_id); status=p.get("status")
 if status not in dict(Reservation.STATUSES):return JsonResponse({"ok":False,"error":"Invalid status."},status=400)
 r.status=status;r.save();return JsonResponse({"ok":True,"status":status})
@login_required
@csrf_exempt
@require_POST
def update_review_status(request,item_id):
 try:p=json.loads(request.body)
 except:return JsonResponse({"ok":False,"error":"Invalid request."},status=400)
 r=get_object_or_404(Review,pk=item_id); status=p.get("status")
 if status not in dict(Review.STATUSES):return JsonResponse({"ok":False,"error":"Invalid status."},status=400)
 r.status=status;r.save();return JsonResponse({"ok":True,"status":status})
