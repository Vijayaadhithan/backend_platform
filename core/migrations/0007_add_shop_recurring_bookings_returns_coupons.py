from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
from django.core.validators import FileExtensionValidator


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_rename_description_de_product_description_ta_and_more'),
    ]

    operations = [
        # Add recurring booking fields
        migrations.AddField(
            model_name='booking',
            name='recurrence_rule',
            field=models.CharField(choices=[('D', 'Daily'), ('W', 'Weekly'), ('M', 'Monthly'), ('Y', 'Yearly'), ('N', 'None')], default='N', max_length=1),
        ),
        migrations.AddField(
            model_name='booking',
            name='recurrence_end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='parent_booking',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recurring_bookings', to='core.booking'),
        ),
        migrations.AddField(
            model_name='booking',
            name='is_recurring_instance',
            field=models.BooleanField(default=False),
        ),
        
        # Create Shop model
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('address', models.TextField()),
                ('contact_info', models.CharField(max_length=255)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='shop_logos/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('rating', models.FloatField(default=0.0)),
                ('total_ratings', models.PositiveIntegerField(default=0)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_shops', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        
        # Add shop field to Product
        migrations.AddField(
            model_name='product',
            name='shop',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='core.shop'),
        ),
        
        # Add shop and rejection fields to Order
        migrations.AddField(
            model_name='order',
            name='shop',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.shop'),
        ),
        migrations.AddField(
            model_name='order',
            name='rejection_reason',
            field=models.CharField(blank=True, choices=[('OOS', 'Out of Stock'), ('INV', 'Invalid Address'), ('PAY', 'Payment Issue'), ('OTH', 'Other')], max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='rejection_details',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('P', 'Pending'), ('S', 'Shipped'), ('D', 'Delivered'), ('C', 'Cancelled'), ('R', 'Rejected')], default='P', max_length=1),
        ),
        
        # Create ReturnRequest model
        migrations.CreateModel(
            name='ReturnRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(choices=[('DMG', 'Damaged Product'), ('WRG', 'Wrong Product'), ('DEF', 'Defective Product'), ('OTH', 'Other')], max_length=3)),
                ('details', models.TextField()),
                ('status', models.CharField(choices=[('P', 'Pending'), ('A', 'Approved'), ('R', 'Rejected'), ('C', 'Completed')], default='P', max_length=1)),
                ('evidence_images', models.JSONField(default=list, help_text='List of image URLs as evidence')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('refund_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('refund_id', models.CharField(blank=True, max_length=255, null=True)),
                ('admin_notes', models.TextField(blank=True, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='return_requests', to='core.order')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('items', models.ManyToManyField(related_name='return_requests', to='core.orderitem')),
            ],
        ),
        
        # Create Coupon model
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True)),
                ('description', models.TextField()),
                ('discount_type', models.CharField(choices=[('P', 'Percentage'), ('F', 'Fixed Amount'), ('S', 'Free Shipping')], max_length=1)),
                ('discount_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('min_purchase_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('valid_from', models.DateTimeField()),
                ('valid_until', models.DateTimeField()),
                ('max_uses', models.PositiveIntegerField(default=1)),
                ('current_uses', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('applies_to_products', models.ManyToManyField(blank=True, related_name='applicable_coupons', to='core.product')),
                ('applies_to_categories', models.ManyToManyField(blank=True, related_name='applicable_coupons', to='core.productcategory')),
                ('applies_to_shops', models.ManyToManyField(blank=True, related_name='applicable_coupons', to='core.shop')),
            ],
        ),
        
        # Create CouponUsage model
        migrations.CreateModel(
            name='CouponUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('used_at', models.DateTimeField(auto_now_add=True)),
                ('discount_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usages', to='core.coupon')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.order')),
                ('booking', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.booking')),
            ],
        ),
        
        # Create AuditLog model
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_type', models.CharField(max_length=255)),
                ('object_id', models.PositiveIntegerField()),
                ('action', models.CharField(choices=[('C', 'Create'), ('U', 'Update'), ('D', 'Delete')], max_length=1)),
                ('changes', models.JSONField(default=dict)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
            ],
        ),
    ]