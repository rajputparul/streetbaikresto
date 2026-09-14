# Street Baik Resto Cafe — Django Full-Stack Ordering Website

This is the Django conversion of the Street Baik cafe website. It includes a responsive customer site, database-backed menu/orders/reservations/reviews/messages, customer order tracking, protected staff dashboard, Django admin, 4 km delivery-location validation, and Twilio WhatsApp notification integration.

## Setup
1. Create a virtual environment.
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill WhatsApp credentials when ready.
4. `python manage.py migrate`
5. `python manage.py seed_menu`
6. `python manage.py createsuperuser`
7. `python manage.py runserver`
8. Customer site: `http://127.0.0.1:8000/`
9. Staff dashboard: `http://127.0.0.1:8000/staff/`
10. Django admin: `http://127.0.0.1:8000/admin/`

## WhatsApp
The order-created and order-status notification code is wired for Twilio WhatsApp. Real messages require a WhatsApp-enabled Twilio sender and credentials in `.env`. The app logs notification status instead of pretending a message was delivered when credentials are absent.

## Production
Set DEBUG=0, use a strong secret, configure ALLOWED_HOSTS, HTTPS, a production database, static collection, and real payment gateway credentials before accepting online payments.


## Client-ready updates

This version is configured for **Dine-in + Takeaway only**. Delivery ordering and customer GPS/location verification have been removed from the customer checkout flow and order API.

### Homepage refresh
- Removed the repeated Street Baik logo from the hero section.
- Added a food-focused hero collage using the existing burger, fries and drink images.
- Simplified the hero actions to **Explore Menu** and **Book a Table**.
- Added clear Dine-in + Takeaway messaging.

### Checkout refresh
- Order type is now **Takeaway** or **Dine-in**.
- Removed delivery address, delivery instructions and location verification.
- Table number is optional for Dine-in (useful when a customer is already seated).
- Existing cart, order tracking, staff dashboard and reservations remain available.

### Location note
The physical cafe address and Maps button remain on the Contact section because customers still need the cafe location for **Dine-in and Takeaway pickup**. Only GPS verification for delivery has been removed.
