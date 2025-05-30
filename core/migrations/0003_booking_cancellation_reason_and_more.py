# Generated by Django 5.1.5 on 2025-03-15 16:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_remove_product_image_url_payment_discount_amount_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="cancellation_reason",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="booking",
            name="notification_sent",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="booking",
            name="preferred_alternate_times",
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name="booking",
            name="waitlist_position",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="average_rating",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=3),
        ),
        migrations.AddField(
            model_name="product",
            name="total_reviews",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="completion_rate",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="featured_rank",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="rating_breakdown",
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="response_time",
            field=models.DurationField(default=datetime.timedelta(days=1)),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="total_ratings",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="verification_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="verification_documents",
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="verification_status",
            field=models.CharField(
                choices=[("P", "Pending"), ("V", "Verified"), ("R", "Rejected")],
                default="P",
                max_length=2,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="last_tier_update",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="loyalty_points",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="user",
            name="notification_preferences",
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name="user",
            name="points_expiry",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="total_spent",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name="booking",
            name="status",
            field=models.CharField(
                choices=[
                    ("P", "Pending"),
                    ("C", "Confirmed"),
                    ("X", "Cancelled"),
                    ("D", "Completed"),
                    ("W", "Waitlisted"),
                    ("R", "Rescheduled"),
                ],
                default="P",
                max_length=1,
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="sku",
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="membership_status",
            field=models.CharField(
                choices=[
                    ("B", "Bronze"),
                    ("S", "Silver"),
                    ("G", "Gold"),
                    ("P", "Platinum"),
                ],
                default="B",
                max_length=1,
            ),
        ),
    ]
