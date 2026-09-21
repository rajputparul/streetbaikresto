import json

from django.test import TestCase

from .models import MenuItem, Order


class OrderFlowTests(TestCase):
    def setUp(self):
        self.item = MenuItem.objects.create(
            id="test-burger",
            category="Burgers",
            name="Test Burger",
            price=99,
            image="burger.jpg",
            description="Test item",
            diet="nonveg",
            active=True,
        )

    def post_order(self, data):
        return self.client.post("/api/orders/", data=json.dumps(data), content_type="application/json")

    def valid_payload(self, **overrides):
        payload = {
            "name": "Test Customer",
            "phone": "9876543210",
            "order_type": "Delivery",
            "address": "Near Aluva Junction, Kochi",
            "payment_method": "Cash / Pay at Cafe",
            "items": [{"id": self.item.id, "quantity": 2}],
        }
        payload.update(overrides)
        return payload

    def test_rejects_invalid_phone(self):
        response = self.post_order(self.valid_payload(phone="12345"))
        self.assertEqual(response.status_code, 400)
        self.assertIn("10 digits", response.json()["error"])

    def test_rejects_short_delivery_address(self):
        response = self.post_order(self.valid_payload(address="Short"))
        self.assertEqual(response.status_code, 400)
        self.assertIn("delivery address", response.json()["error"].lower())

    def test_creates_order_with_public_id(self):
        response = self.post_order(self.valid_payload())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["public_id"].startswith("SBK-"))
        order = Order.objects.get(public_id=data["public_id"])
        self.assertEqual(order.status, "Order Received")
        self.assertEqual(order.items_json[0]["quantity"], 2)

    def test_invalid_order_tracking_returns_json_404(self):
        response = self.client.get("/api/orders/SBK-NOT-REAL/")
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()["ok"])
