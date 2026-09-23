import base64
import json
import secrets
import urllib.parse
import urllib.request

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .models import MenuItem, Message, NotificationLog, Order, Reservation, Review


def whatsapp_url(message):
    phone = "".join(ch for ch in settings.CLIENT_WHATSAPP if ch.isdigit())
    if len(phone) == 10:
        phone = "91" + phone
    return "https://wa.me/" + phone + "?text=" + urllib.parse.quote(message)


def gallery_media():
    return {
        "photos": [
            "burger.jpg",
            "chicken-category.jpg",
            "fries.jpg",
            "shawarma.jpg",
            "mojito.jpg",
            "drinks-category.jpg",
            "photo/about.jpg",
            "photo/2.jpg",
            "photo/3.webp",
        ],
        "videos": [
            "photo/video/WhatsApp Video 2026-08-06 at 9.54.03 PM.mp4",
            "photo/video/WhatsApp Video 2026-08-06 at 9.54.02 PM.mp4",
            "photo/video/WhatsApp Video 2026-08-06 at 9.54.01 PM.mp4",
        ],
    }


def categories():
    names = [
        ("All", "all"),
        ("Burgers", "burger-category.jpg"),
        ("Chef Special", "chicken-category.jpg"),
        ("Combos", "burger-category.jpg"),
        ("Hot & Crispy", "chicken-category.jpg"),
        ("Drinks", "drinks-category.jpg"),
        ("Frappes", "drinks-category.jpg"),
        ("Shakes", "drinks-category.jpg"),
    ]
    return [{"name": name, "image": image, "icon": ""} for name, image in names]


@ensure_csrf_cookie
def home(request):
    return render(
        request,
        "index.html",
        {
            "categories": categories(),
            "gallery": gallery_media(),
            "support_whatsapp": whatsapp_url(
                "Hi Street Baik, I need help with my order."
            ),
            "menu_whatsapp": whatsapp_url(
                "Hi Street Baik, I have a question about the menu."
            ),
            "delivery_radius_km": settings.DELIVERY_RADIUS_KM,
        },
    )


def customer_login(request):
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        user = User.objects.filter(
            email__iexact=email,
            is_staff=False
        ).first()

        if user and user.check_password(password):
            login(request, user)
            return redirect("home")

        return render(
            request,
            "auth.html",
            {
                "mode": "login",
                "error": "We couldn't match that email and password.",
            },
        )

    return render(request, "auth.html", {"mode": "login"})


def customer_register(request):
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        if not name or not email or len(password) < 8:
            return render(
                request,
                "auth.html",
                {
                    "mode": "register",
                    "error": (
                        "Add your name, a valid email and a password "
                        "of at least 8 characters."
                    ),
                },
            )

        if User.objects.filter(email__iexact=email).exists():
            return render(
                request,
                "auth.html",
                {
                    "mode": "register",
                    "error": "An account already exists for that email.",
                },
            )

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name,
        )

        login(request, user)
        return redirect("home")

    return render(request, "auth.html", {"mode": "register"})


def customer_logout(request):
    logout(request)
    return redirect("home")


@ensure_csrf_cookie
def track(request):
    return render(
        request,
        "track.html",
        {
            "support_whatsapp": whatsapp_url(
                "Hi Street Baik, I need help tracking my order."
            )
        },
    )


def api_menu(request):
    return JsonResponse(
        {
            "items": list(
                MenuItem.objects.filter(active=True).values()
            ),
            "categories": categories(),
        }
    )


def new_id(prefix="SB"):
    if prefix == "SB":
        prefix = "SBK"

    while True:
        stamp = __import__("datetime").datetime.now().strftime("%Y%m%d")
        public_id = f"{prefix}-{stamp}-{secrets.randbelow(9000) + 1000}"

        if not Order.objects.filter(public_id=public_id).exists():
            return public_id


def request_host(order):
    if settings.SITE_URL:
        return (
            f"{settings.SITE_URL.rstrip('/')}"
            f"/track/?order={order.public_id}"
        )

    return "Configure SITE_URL in production"


def send_whatsapp(order, event):
    msg = (
        f"Street Baik - "
        f"{'NEW ORDER' if event == 'order_created' else 'ORDER UPDATE'}\n"
        f"Order: {order.public_id}\n"
        f"Customer: {order.customer_name}\n"
        f"Phone: {order.phone}\n"
        f"Type: {order.order_type}\n"
        f"Total: Rs {order.total:.0f}\n"
        f"Status: {order.status}\n"
        f"Track: {request_host(order)}"
    )

    sid = settings.TWILIO_ACCOUNT_SID
    token = settings.TWILIO_AUTH_TOKEN
    sender = settings.TWILIO_WHATSAPP_FROM
    to = settings.CLIENT_WHATSAPP

    if not all([sid, token, sender, to]):
        NotificationLog.objects.create(
            order=order,
            channel="WhatsApp",
            event=event,
            status="Not configured",
            detail=(
                "Add Twilio WhatsApp credentials and "
                "CLIENT_WHATSAPP to .env"
            ),
        )
        return False

    try:
        data = urllib.parse.urlencode(
            {
                "To": "whatsapp:+91"
                + to.replace("+91", "").replace(" ", ""),
                "From": "whatsapp:"
                + sender.replace("whatsapp:", ""),
                "Body": msg,
            }
        ).encode()

        auth = base64.b64encode(
            f"{sid}:{token}".encode()
        ).decode()

        req = urllib.request.Request(
            f"https://api.twilio.com/2010-04-01/"
            f"Accounts/{sid}/Messages.json",
            data=data,
            headers={
                "Authorization": "Basic " + auth
            },
        )

        urllib.request.urlopen(req, timeout=10).read()

        NotificationLog.objects.create(
            order=order,
            channel="WhatsApp",
            event=event,
            status="Sent",
        )

        return True

    except Exception as exc:
        NotificationLog.objects.create(
            order=order,
            channel="WhatsApp",
            event=event,
            status="Failed",
            detail=str(exc)[:500],
        )

        return False


@require_POST
def create_order(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {
                "ok": False,
                "error": "Invalid request.",
            },
            status=400,
        )

    required = [
        "name",
        "phone",
        "order_type",
        "items",
        "payment_method",
    ]

    if any(not payload.get(field) for field in required):
        return JsonResponse(
            {
                "ok": False,
                "error": "Please fill all required order details.",
            },
            status=400,
        )

    phone = str(payload["phone"]).strip()

    if not phone.isdigit() or len(phone) != 10:
        return JsonResponse(
            {
                "ok": False,
                "error": "Phone number must contain exactly 10 digits.",
            },
            status=400,
        )

    # Only Takeaway and Dine-in are allowed.
    order_type = payload["order_type"]

    if order_type not in ["Takeaway", "Dine-in"]:
        return JsonResponse(
            {
                "ok": False,
                "error": "Please choose Takeaway or Dine-in.",
            },
            status=400,
        )

    # Delivery is no longer supported.
    address = ""

    clean_items = []
    subtotal = 0

    for row in payload["items"]:
        item = MenuItem.objects.filter(
            pk=str(row.get("id")),
            active=True,
        ).first()

        try:
            quantity = int(row.get("quantity", 0))
        except (TypeError, ValueError):
            quantity = 0

        if not item or quantity < 1 or quantity > 99:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "Invalid cart item.",
                },
                status=400,
            )

        line_total = float(item.price) * quantity
        subtotal += line_total

        clean_items.append(
            {
                "id": item.id,
                "name": item.name,
                "price": float(item.price),
                "quantity": quantity,
                "line_total": line_total,
            }
        )

    order = Order.objects.create(
        public_id=new_id(),
        customer_name=payload["name"].strip(),
        email=payload.get("email", "").strip(),
        phone=phone,
        address=address,
        order_type=order_type,
        table_no=str(
            payload.get("table_no", "")
        ).strip(),
        instructions=str(
            payload.get("instructions", "")
        ).strip(),
        latitude=None,
        longitude=None,
        subtotal=subtotal,
        total=subtotal,
        payment_method=payload["payment_method"],
        items_json=clean_items,
        status="Order Received",
    )

    send_whatsapp(order, "order_created")

    return JsonResponse(
        {
            "ok": True,
            "public_id": order.public_id,
            "total": float(order.total),
            "status": order.status,
        }
    )


def get_order(request, public_id):
    order = Order.objects.filter(
        public_id=public_id.upper()
    ).first()

    if not order:
        return JsonResponse(
            {
                "ok": False,
                "error": "No order found for that Order ID.",
            },
            status=404,
        )

    data = {
        "public_id": order.public_id,
        "customer_name": order.customer_name,
        "order_type": order.order_type,
        "total": float(order.total),
        "status": order.status,
        "items": order.items_json,
        "updated_at": order.updated_at.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    }

    return JsonResponse(
        {
            "ok": True,
            "order": data,
            "statuses": [
                status[0]
                for status in Order.STATUSES
            ],
        }
    )


@require_POST
def create_reservation(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {
                "ok": False,
                "error": "Invalid request.",
            },
            status=400,
        )

    if not all(
        payload.get(field)
        for field in [
            "name",
            "phone",
            "date",
            "time",
            "guests",
        ]
    ):
        return JsonResponse(
            {
                "ok": False,
                "error": "Please fill all required reservation fields.",
            },
            status=400,
        )

    phone = str(payload["phone"]).strip()

    if not phone.isdigit() or len(phone) != 10:
        return JsonResponse(
            {
                "ok": False,
                "error": "Phone number must contain exactly 10 digits.",
            },
            status=400,
        )

    reservation = Reservation.objects.create(
        booking_id=new_id("TB"),
        name=payload["name"].strip(),
        phone=phone,
        email=payload.get("email", "").strip(),
        date=payload["date"],
        time=payload["time"],
        guests=int(payload["guests"]),
        request=payload.get("request", "").strip(),
    )

    return JsonResponse(
        {
            "ok": True,
            "booking_id": reservation.booking_id,
            "status": reservation.status,
        }
    )


@require_POST
def create_review(request):
    try:
        payload = json.loads(request.body)
        rating = int(payload.get("rating", 0))
    except (json.JSONDecodeError, ValueError):
        return JsonResponse(
            {
                "ok": False,
                "error": "Invalid review.",
            },
            status=400,
        )

    if (
        not payload.get("name")
        or rating not in range(1, 6)
        or not payload.get("review")
    ):
        return JsonResponse(
            {
                "ok": False,
                "error": "Please provide name, rating and review.",
            },
            status=400,
        )

    Review.objects.create(
        name=payload["name"].strip(),
        rating=rating,
        review=payload["review"].strip(),
    )

    return JsonResponse({"ok": True})


@require_POST
def create_message(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {
                "ok": False,
                "error": "Invalid request.",
            },
            status=400,
        )

    if not payload.get("name") or not payload.get("message"):
        return JsonResponse(
            {
                "ok": False,
                "error": "Name and message are required.",
            },
            status=400,
        )

    Message.objects.create(
        name=payload["name"].strip(),
        email=payload.get("email", "").strip(),
        phone=payload.get("phone", "").strip(),
        message=payload["message"].strip(),
    )

    return JsonResponse({"ok": True})


def staff_login(request):
    if request.user.is_authenticated:
        return staff_dashboard(request)

    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )

        if user and user.is_staff:
            login(request, user)
            return redirect("staff")

        return render(
            request,
            "admin.html",
            {
                "error": "Invalid username or password."
            },
        )

    return render(
        request,
        "admin.html",
        {
            "error": None
        },
    )


def staff_logout(request):
    logout(request)
    return redirect("staff")


@login_required
@ensure_csrf_cookie
def staff_dashboard(request):
    if not request.user.is_staff:
        return redirect("home")

    orders = Order.objects.all().order_by("-created_at")
    reservations = Reservation.objects.all().order_by("-created_at")
    reviews = Review.objects.all().order_by("-created_at")
    messages = Message.objects.all().order_by("-created_at")

    stats = {
        "orders": orders.count(),
        "pending": orders.filter(
            status="Order Received"
        ).count(),
        "revenue": orders.filter(
            status__in=[
                "Confirmed",
                "Preparing",
                "Ready",
                "Out for Delivery",
                "Delivered",
            ]
        ).aggregate(
            x=Sum("total")
        )["x"] or 0,
        "reservations": reservations.count(),
        "reviews": reviews.count(),
        "messages": messages.count(),
    }

    return render(
        request,
        "admin.html",
        {
            "logged_in": True,
            "orders": orders,
            "reservations": reservations,
            "reviews": reviews,
            "messages": messages,
            "stats": stats,
            "statuses": [
                status[0]
                for status in Order.STATUSES
            ],
        },
    )


@login_required
@require_POST
def update_order_status(request, order_id):
    if not request.user.is_staff:
        return JsonResponse(
            {
                "ok": False,
                "error": "Staff access required.",
            },
            status=403,
        )

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {
                "ok": False,
                "error": "Invalid request.",
            },
            status=400,
        )

    status = payload.get("status")
    order = get_object_or_404(Order, pk=order_id)

    if status not in dict(Order.STATUSES):
        return JsonResponse(
            {
                "ok": False,
                "error": "Invalid status.",
            },
            status=400,
        )

    order.status = status
    order.save()

    send_whatsapp(
        order,
        "status_" + status.lower().replace(" ", "_")
    )

    return JsonResponse(
        {
            "ok": True,
            "status": status,
        }
    )


@login_required
@require_POST
def update_reservation_status(request, item_id):
    if not request.user.is_staff:
        return JsonResponse(
            {
                "ok": False,
                "error": "Staff access required.",
            },
            status=403,
        )

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {
                "ok": False,
                "error": "Invalid request.",
            },
            status=400,
        )

    reservation = get_object_or_404(
        Reservation,
        pk=item_id,
    )

    status = payload.get("status")

    if status not in dict(Reservation.STATUSES):
        return JsonResponse(
            {
                "ok": False,
                "error": "Invalid status.",
            },
            status=400,
        )

    reservation.status = status
    reservation.save()

    return JsonResponse(
        {
            "ok": True,
            "status": status,
        }
    )


@login_required
@require_POST
def update_review_status(request, item_id):
    if not request.user.is_staff:
        return JsonResponse(
            {
                "ok": False,
                "error": "Staff access required.",
            },
            status=403,
        )

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {
                "ok": False,
                "error": "Invalid request.",
            },
            status=400,
        )

    review = get_object_or_404(
        Review,
        pk=item_id,
    )

    status = payload.get("status")

    if status not in dict(Review.STATUSES):
        return JsonResponse(
            {
                "ok": False,
                "error": "Invalid status.",
            },
            status=400,
        )

    review.status = status
    review.save()

    return JsonResponse(
        {
            "ok": True,
            "status": status,
        }
    )