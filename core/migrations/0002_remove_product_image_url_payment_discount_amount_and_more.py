# Generated by Django 5.1.5 on 2025-03-15 16:23

import core.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="image_url",
        ),
        migrations.AddField(
            model_name="payment",
            name="discount_amount",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="payment",
            name="gst_amount",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="payment",
            name="refund_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="gallery_images",
            field=models.JSONField(
                default=list, help_text="List of additional product image URLs"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="product",
            name="main_image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="products/",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        ["jpg", "jpeg", "png"]
                    ),
                    core.models.validate_file_size,
                ],
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="max_order_quantity",
            field=models.PositiveIntegerField(default=100),
        ),
        migrations.AddField(
            model_name="product",
            name="min_order_quantity",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="product",
            name="sku",
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="product",
            name="weight",
            field=models.DecimalField(
                decimal_places=2, default=0.1, help_text="Weight in kg", max_digits=6
            ),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="cancellation_policy",
            field=models.TextField(default="24 hours notice required for cancellation"),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="gallery_images",
            field=models.JSONField(
                default=list, help_text="List of image URLs showing past work"
            ),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="is_verified",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="max_booking_per_slot",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="profile_image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="service_providers/",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        ["jpg", "jpeg", "png"]
                    ),
                    core.models.validate_file_size,
                ],
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="payment_method",
            field=models.CharField(
                choices=[
                    ("CC", "Credit Card"),
                    ("DC", "Debit Card"),
                    ("UPI", "UPI"),
                    ("NB", "Net Banking"),
                    ("WL", "Wallet"),
                ],
                max_length=3,
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="status",
            field=models.CharField(
                choices=[
                    ("P", "Pending"),
                    ("S", "Success"),
                    ("F", "Failed"),
                    ("R", "Refunded"),
                ],
                default="P",
                max_length=1,
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="transaction_id",
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="profile_picture",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="profiles/",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        ["jpg", "jpeg", "png"]
                    ),
                    core.models.validate_file_size,
                ],
            ),
        ),
    ]
