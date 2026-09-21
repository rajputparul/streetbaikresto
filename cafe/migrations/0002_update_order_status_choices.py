from django.db import migrations, models


def forwards(apps, schema_editor):
    Order = apps.get_model("cafe", "Order")
    Order.objects.filter(status="Pending").update(status="Order Received")
    Order.objects.filter(status="Completed").update(status="Delivered")


def backwards(apps, schema_editor):
    Order = apps.get_model("cafe", "Order")
    Order.objects.filter(status="Order Received").update(status="Pending")
    Order.objects.filter(status="Delivered").update(status="Completed")


class Migration(migrations.Migration):
    dependencies = [
        ("cafe", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("Order Received", "Order Received"),
                    ("Confirmed", "Confirmed"),
                    ("Preparing", "Preparing"),
                    ("Ready", "Ready"),
                    ("Out for Delivery", "Out for Delivery"),
                    ("Delivered", "Delivered"),
                    ("Cancelled", "Cancelled"),
                ],
                default="Order Received",
                max_length=30,
            ),
        ),
    ]
