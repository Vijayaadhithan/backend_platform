from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
import os

def validate_file_size(value):
    max_size = 5 * 1024 * 1024  # 5MB
    if value.size > max_size:
        raise ValidationError(f'File size cannot exceed {max_size/1024/1024}MB')

def validate_image_extension(value):
    valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
    ext = os.path.splitext(value.name)[1][1:].lower()
    if ext not in valid_extensions:
        raise ValidationError(f'Unsupported file extension. Allowed extensions are: {", ".join(valid_extensions)}')


class User(AbstractUser):
    MEMBERSHIP_CHOICES = [('B', 'Bronze'), ('S', 'Silver'), ('G', 'Gold'), ('P', 'Platinum')]
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('ta', 'Tamil'),
        ('hi', 'Hindi'),
    ]
    
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    profile_picture = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png']), validate_file_size]
    )
    membership_status = models.CharField(max_length=1, choices=MEMBERSHIP_CHOICES, default='B')
    loyalty_points = models.PositiveIntegerField(default=0)
    points_expiry = models.DateTimeField(null=True, blank=True)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_tier_update = models.DateTimeField(null=True, blank=True)
    notification_preferences = models.JSONField(default=dict)
    date_joined = models.DateTimeField(default=timezone.now)
    language_preference = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    groups = models.ManyToManyField(Group, related_name='core_user_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='core_user_permissions')

    def update_membership_tier(self):
        if self.total_spent >= 5000:
            self.membership_status = 'P'
        elif self.total_spent >= 2000:
            self.membership_status = 'G'
        elif self.total_spent >= 500:
            self.membership_status = 'S'
        self.last_tier_update = timezone.now()
        self.save()

    def add_loyalty_points(self, amount_spent):
        points_earned = int(amount_spent * 10)  # 10 points per currency unit
        self.loyalty_points += points_earned
        if not self.points_expiry:
            self.points_expiry = timezone.now() + timezone.timedelta(days=365)
        self.total_spent += Decimal(amount_spent)
        self.update_membership_tier()
        return points_earned

class ServiceProvider(models.Model):
    SERVICE_TYPES = [('H', 'Home'), ('E', 'Event'), ('P', 'Personal')]
    
    name = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255)
    service_type = models.CharField(max_length=1, choices=SERVICE_TYPES)
    location = models.CharField(max_length=255)
    rating = models.FloatField(default=0.0)
    total_ratings = models.PositiveIntegerField(default=0)
    rating_breakdown = models.JSONField(default=dict)  # Store counts for each star rating
    certifications = models.TextField()
    verification_status = models.CharField(
        max_length=2,
        choices=[('P', 'Pending'), ('V', 'Verified'), ('R', 'Rejected')],
        default='P'
    )
    verification_date = models.DateTimeField(null=True, blank=True)
    verification_documents = models.JSONField(default=list)
    availability = models.JSONField(default=dict)
    profile_image = models.ImageField(
        upload_to='service_providers/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png']), validate_file_size]
    )
    gallery_images = models.JSONField(
        default=list,
        help_text='List of image URLs showing past work'
    )
    is_verified = models.BooleanField(default=False)
    max_booking_per_slot = models.PositiveIntegerField(default=1)
    cancellation_policy = models.TextField(default='24 hours notice required for cancellation')
    featured_rank = models.PositiveIntegerField(null=True, blank=True)  # For promoting top providers
    response_time = models.DurationField(default=timezone.timedelta(hours=24))
    completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    def clean(self):
        super().clean()
        # Validate availability format
        if not isinstance(self.availability, dict):
            raise ValidationError({'availability': 'Availability must be a dictionary'})
        # Validate booking slots
        if self.max_booking_per_slot < 1:
            raise ValidationError({'max_booking_per_slot': 'Must allow at least one booking per slot'})

    def update_rating(self, new_rating):
        self.total_ratings += 1
        # Update rating breakdown
        breakdown = self.rating_breakdown or {}
        breakdown[str(new_rating)] = breakdown.get(str(new_rating), 0) + 1
        self.rating_breakdown = breakdown
        # Update average rating
        self.rating = ((self.rating * (self.total_ratings - 1)) + new_rating) / self.total_ratings
        self.save()

    def update_completion_rate(self):
        total_bookings = Booking.objects.filter(service_provider=self).count()
        completed_bookings = Booking.objects.filter(
            service_provider=self,
            status='D'
        ).count()
        if total_bookings > 0:
            self.completion_rate = (completed_bookings / total_bookings) * 100
            self.save()

class ServiceType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

class Booking(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'), ('C', 'Confirmed'),
        ('X', 'Cancelled'), ('D', 'Completed'),
        ('W', 'Waitlisted'), ('R', 'Rescheduled')
    ]
    
    RECURRENCE_CHOICES = [
        ('D', 'Daily'), ('W', 'Weekly'),
        ('M', 'Monthly'), ('Y', 'Yearly'),
        ('N', 'None')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    duration = models.DurationField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    review = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    waitlist_position = models.PositiveIntegerField(null=True, blank=True)
    preferred_alternate_times = models.JSONField(default=list)
    notification_sent = models.BooleanField(default=False)
    cancellation_reason = models.TextField(null=True, blank=True)
    
    # Recurring booking fields
    recurrence_rule = models.CharField(max_length=1, choices=RECURRENCE_CHOICES, default='N')
    recurrence_end_date = models.DateTimeField(null=True, blank=True)
    parent_booking = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='recurring_bookings')
    is_recurring_instance = models.BooleanField(default=False)

    def move_to_waitlist(self):
        existing_waitlist = Booking.objects.filter(
            service_provider=self.service_provider,
            scheduled_time=self.scheduled_time,
            status='W'
        ).count()
        self.waitlist_position = existing_waitlist + 1
        self.status = 'W'
        self.save()

    def process_waitlist(self):
        if self.status == 'X':
            # Find next waitlisted booking
            next_in_line = Booking.objects.filter(
                service_provider=self.service_provider,
                scheduled_time=self.scheduled_time,
                status='W'
            ).order_by('waitlist_position').first()
            
            if next_in_line:
                next_in_line.status = 'C'
                next_in_line.waitlist_position = None
                next_in_line.save()
                
                # Update remaining waitlist positions
                Booking.objects.filter(
                    service_provider=self.service_provider,
                    scheduled_time=self.scheduled_time,
                    status='W',
                    waitlist_position__gt=next_in_line.waitlist_position
                ).update(waitlist_position=models.F('waitlist_position') - 1)

    def clean(self):
        super().clean()
        # Validate booking time
        if self.scheduled_time <= timezone.now():
            raise ValidationError({'scheduled_time': 'Booking time must be in the future'})

        # Check service provider availability
        day_str = self.scheduled_time.strftime('%Y-%m-%d')
        if day_str not in self.service_provider.availability:
            raise ValidationError({'scheduled_time': 'Service provider is not available on this day'})

        # Check existing bookings for this slot
        existing_bookings = Booking.objects.filter(
            service_provider=self.service_provider,
            scheduled_time=self.scheduled_time
        ).count()
        if existing_bookings >= self.service_provider.max_booking_per_slot:
            raise ValidationError({'scheduled_time': 'This time slot is fully booked'})

    def save(self, *args, **kwargs):
        self.full_clean()
        from django.db.models import Count
        from django.utils import timezone
        from decimal import Decimal
        
        # Calculate base price based on service type and duration
        hours = self.duration.total_seconds() / 3600
        base_cost = self.service_type.base_price
        hourly_rate = self.service_type.unit_price
        
        # Dynamic pricing based on demand
        today = timezone.now().date()
        bookings_today = Booking.objects.filter(
            service_type=self.service_type,
            scheduled_time__date=today
        ).count()
        
        # Surge pricing based on number of bookings (20% increase if more than 5 bookings)
        surge_multiplier = Decimal('1.2') if bookings_today > 5 else Decimal('1.0')
        
        # Peak hours pricing (10% increase between 9 AM and 6 PM)
        hour = self.scheduled_time.hour
        peak_multiplier = Decimal('1.1') if 9 <= hour <= 18 else Decimal('1.0')
        
        # Calculate initial price
        initial_price = (base_cost + (hourly_rate * hours))
        
        # Apply surge and peak pricing
        price_after_surge = initial_price * surge_multiplier * peak_multiplier
        
        # Apply membership discount
        if self.user.membership_status == 'P':
            discount = Decimal('0.15')  # 15% discount for premium members
        else:
            discount = Decimal('0.0')
        
        self.price = price_after_surge * (1 - discount)
        super().save(*args, **kwargs)

class ProductCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    main_image = models.ImageField(
        upload_to='products/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png']), validate_file_size],
        null=True,
        blank=True
    )
    gallery_images = models.JSONField(
        default=list,
        help_text='List of additional product image URLs'
    )
    sku = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    min_order_quantity = models.PositiveIntegerField(default=1)
    max_order_quantity = models.PositiveIntegerField(default=100)
    weight = models.DecimalField(max_digits=6, decimal_places=2, help_text='Weight in kg', default=0.1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.sku:
            # Generate SKU: Category prefix + Sequential number
            prefix = self.category.name[:3].upper()
            last_product = Product.objects.filter(sku__startswith=prefix).order_by('-sku').first()
            if last_product:
                last_number = int(last_product.sku[3:])
                new_number = last_number + 1
            else:
                new_number = 1
            self.sku = f"{prefix}{new_number:06d}"
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.stock_quantity < 0:
            raise ValidationError({'stock_quantity': 'Stock quantity cannot be negative'})
        if self.min_order_quantity > self.max_order_quantity:
            raise ValidationError({'min_order_quantity': 'Minimum order quantity cannot be greater than maximum order quantity'})
        if not self.is_active and self.stock_quantity > 0:
            raise ValidationError({'is_active': 'Products with stock must remain active'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Order(models.Model):
    STATUS_CHOICES = [('P', 'Pending'), ('S', 'Shipped'), ('D', 'Delivered'), ('C', 'Cancelled'), ('R', 'Rejected')]
    REJECTION_CHOICES = [
        ('OOS', 'Out of Stock'),
        ('INV', 'Invalid Address'),
        ('PAY', 'Payment Issue'),
        ('OTH', 'Other')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    rejection_reason = models.CharField(max_length=3, choices=REJECTION_CHOICES, null=True, blank=True)
    rejection_details = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Update product stock on order status change
        if self.pk:
            old_order = Order.objects.get(pk=self.pk)
            if old_order.status != self.status and self.status == 'D':
                # Reduce stock when order is delivered
                for item in self.orderitem_set.all():
                    product = item.product
                    product.stock_quantity -= item.quantity
                    if product.stock_quantity < 0:
                        raise ValidationError(f'Insufficient stock for product {product.name}')
                    product.save()
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('P', 'Pending'),
        ('S', 'Success'),
        ('F', 'Failed'),
        ('R', 'Refunded')
    ]
    PAYMENT_METHODS = [
        ('CC', 'Credit Card'),
        ('DC', 'Debit Card'),
        ('UPI', 'UPI'),
        ('NB', 'Net Banking'),
        ('WL', 'Wallet')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.SET_NULL)
    booking = models.ForeignKey(Booking, null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=3, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=1, choices=PAYMENT_STATUS, default='P')
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.gst_amount:
            # Calculate GST based on Indian tax rules
            # For services (booking)
            if self.booking:
                # 18% GST for services
                self.gst_amount = self.amount * Decimal('0.18')
            # For products (order)
            elif self.order:
                # Calculate GST based on product category (example rates)
                total_gst = Decimal('0')
                for item in self.order.orderitem_set.all():
                    if item.product.price <= 1000:
                        # 5% GST for products under ₹1000
                        gst_rate = Decimal('0.05')
                    else:
                        # 12% GST for products over ₹1000
                        gst_rate = Decimal('0.12')
                    total_gst += item.price * gst_rate
                self.gst_amount = total_gst
        super().save(*args, **kwargs)

class Membership(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    benefits = models.TextField()

class UserMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, default='Active')

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(max_length=20)
    status = models.CharField(max_length=10, default='Unread')
    created_at = models.DateTimeField(auto_now_add=True)

class LoyaltyProgram(models.Model):
    TIER_CHOICES = [('B', 'Bronze'), ('S', 'Silver'), ('G', 'Gold')]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default=0)
    tier = models.CharField(max_length=1, choices=TIER_CHOICES, default='B')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-points']


class Shop(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    address = models.TextField()
    contact_info = models.CharField(max_length=255)
    logo = models.ImageField(
        upload_to='shop_logos/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png']), validate_file_size]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.FloatField(default=0.0)
    total_ratings = models.PositiveIntegerField(default=0)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_shops')

    def __str__(self):
        return self.name


class ReturnRequest(models.Model):
    REASON_CHOICES = [
        ('DMG', 'Damaged Product'),
        ('WRG', 'Wrong Product'),
        ('DEF', 'Defective Product'),
        ('OTH', 'Other')
    ]
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
        ('C', 'Completed')
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='return_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem, related_name='return_requests')
    reason = models.CharField(max_length=3, choices=REASON_CHOICES)
    details = models.TextField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    evidence_images = models.JSONField(default=list, help_text='List of image URLs as evidence')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    refund_id = models.CharField(max_length=255, null=True, blank=True)
    admin_notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Return #{self.id} for Order #{self.order.id}"

    def process_refund(self):
        """Process refund through Razorpay when return is approved"""
        if self.status == 'A' and not self.refund_id:
            import razorpay
            from django.conf import settings
            
            # Find the payment for this order
            payment = Payment.objects.filter(order=self.order, status='S').first()
            
            if payment:
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                
                try:
                    # Create refund request
                    refund_data = {
                        'payment_id': payment.transaction_id,
                        'amount': int(self.refund_amount * 100),  # Convert to paisa
                        'notes': {
                            'return_request_id': str(self.id),
                            'reason': self.get_reason_display()
                        }
                    }
                    
                    refund = client.refund.create(data=refund_data)
                    
                    # Update return request with refund info
                    self.refund_id = refund['id']
                    self.status = 'C'  # Mark as completed
                    self.save()
                    
                    # Update payment status
                    payment.status = 'R'  # Refunded
                    payment.refund_id = refund['id']
                    payment.save()
                    
                    return True
                except Exception as e:
                    # Log the error
                    self.admin_notes = f"Refund failed: {str(e)}"
                    self.save()
            
        return False


class Coupon(models.Model):
    DISCOUNT_TYPES = [
        ('P', 'Percentage'),
        ('F', 'Fixed Amount'),
        ('S', 'Free Shipping')
    ]
    
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    discount_type = models.CharField(max_length=1, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    max_uses = models.PositiveIntegerField(default=1)
    current_uses = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    applies_to_products = models.ManyToManyField(Product, blank=True, related_name='applicable_coupons')
    applies_to_categories = models.ManyToManyField(ProductCategory, blank=True, related_name='applicable_coupons')
    applies_to_shops = models.ManyToManyField(Shop, blank=True, related_name='applicable_coupons')

    def __str__(self):
        return self.code

    def is_valid(self, user=None, products=None, total_amount=None):
        """Check if coupon is valid for the given context"""
        from django.utils import timezone
        now = timezone.now()
        
        # Basic validity checks
        if not self.is_active:
            return False
        
        if now < self.valid_from or now > self.valid_until:
            return False
        
        if self.current_uses >= self.max_uses:
            return False
        
        # Check minimum purchase amount
        if total_amount and total_amount < self.min_purchase_amount:
            return False
        
        # Check product applicability
        if products and self.applies_to_products.exists():
            applicable_product_ids = set(self.applies_to_products.values_list('id', flat=True))
            product_ids = set(p.id for p in products)
            if not product_ids.intersection(applicable_product_ids):
                return False
        
        return True

    def calculate_discount(self, total_amount):
        """Calculate the discount amount based on coupon type"""
        if self.discount_type == 'P':  # Percentage
            return (self.discount_value / 100) * total_amount
        elif self.discount_type == 'F':  # Fixed amount
            return min(self.discount_value, total_amount)  # Don't exceed total amount
        elif self.discount_type == 'S':  # Free shipping
            # This would depend on shipping cost calculation
            return Decimal('0.00')
        
        return Decimal('0.00')


class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)
    used_at = models.DateTimeField(auto_now_add=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.coupon.code} used by {self.user.username}"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('C', 'Create'),
        ('U', 'Update'),
        ('D', 'Delete')
    ]
    
    content_type = models.CharField(max_length=255)
    object_id = models.PositiveIntegerField()
    action = models.CharField(max_length=1, choices=ACTION_CHOICES)
    changes = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_action_display()} on {self.content_type} #{self.object_id}"
