from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from .models import User, ServiceProvider, ServiceType, Product, Booking, Order, LoyaltyProgram, Membership, UserMembership, Review, Notification
from .serializers import UserSerializer, AuthTokenSerializer, ServiceProviderSerializer, ServiceTypeSerializer, ProductSerializer, BookingSerializer, OrderSerializer, LoyaltyProgramSerializer, MembershipSerializer, UserMembershipSerializer, ReviewSerializer, NotificationSerializer
from datetime import datetime
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from .models import Payment, Booking, Order

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class CreateUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'user': UserSerializer(user).data,
                'token': Token.objects.create(user=user).key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'membership_status': user.membership_status
        })

class PaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from decimal import Decimal
        amount = request.data.get('amount')
        booking_id = request.data.get('booking_id')
        order_id = request.data.get('order_id')

        # Apply membership discount
        if request.user.membership_status == 'P':
            amount = Decimal(str(amount)) * Decimal('0.9')  # 10% discount for premium members

        # Calculate GST (18% on 90% of amount as per Indian regulations)
        base_amount = Decimal(str(amount))
        taxable_amount = base_amount * Decimal('0.9')
        gst = taxable_amount * Decimal('0.18')
        total_amount = int((taxable_amount + gst) * 100)  # Convert to paisa for Razorpay

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        payment_data = {
            'amount': total_amount,
            'currency': 'INR',
            'receipt': f'receipt_{datetime.now().timestamp()}',
            'payment_capture': 1,
            'notes': {'booking_id': booking_id} if booking_id else {'order_id': order_id}
        }

        try:
            order = client.order.create(data=payment_data)
            payment = Payment.objects.create(
                user=request.user,
                booking_id=booking_id,
                order_id=order_id,
                amount=total_amount,
                payment_method='Razorpay',
                transaction_id=order['id'],
                status='Pending'
            )
            return Response({
                'order_id': order['id'],
                'amount': total_amount,
                'currency': 'INR',
                'key': settings.RAZORPAY_KEY_ID
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

from django_filters import rest_framework as filters
from django.db.models import Q
import json

class ServiceProviderFilter(filters.FilterSet):
    location = filters.CharFilter(lookup_expr='icontains')
    rating_min = filters.NumberFilter(field_name='rating', lookup_expr='gte')
    rating_max = filters.NumberFilter(field_name='rating', lookup_expr='lte')
    service_type = filters.CharFilter(field_name='service_type')
    available_date = filters.CharFilter(method='filter_by_availability')
    available_time = filters.TimeFilter(method='filter_by_time')
    
    def filter_by_availability(self, queryset, name, value):
        # Filter providers that have the specified date in their availability JSON
        return queryset.filter(availability__has_key=value)
    
    def filter_by_time(self, queryset, name, value):
        # This is more complex as it requires parsing the JSON structure
        # For each provider, check if the time slot is available on any date
        filtered_providers = []
        for provider in queryset:
            for date, slots in provider.availability.items():
                # Check if the time is in any of the available slots
                for slot in slots:
                    # Assuming slot format is "HH:MM-HH:MM"
                    start_time, end_time = slot.split('-')
                    if start_time <= value.strftime('%H:%M') <= end_time:
                        filtered_providers.append(provider.id)
                        break
        
        return queryset.filter(id__in=filtered_providers)
    
    class Meta:
        model = ServiceProvider
        fields = ['location', 'rating_min', 'rating_max', 'service_type', 'available_date', 'available_time']

class ServiceProviderViewSet(viewsets.ModelViewSet):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ServiceProviderFilter

class ServiceTypeViewSet(viewsets.ModelViewSet):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        recurrence_rule = data.get('recurrence_rule', 'N')
        recurrence_end_date = data.get('recurrence_end_date')
        
        # If not a recurring booking, proceed normally
        if recurrence_rule == 'N' or not recurrence_end_date:
            return super().create(request, *args, **kwargs)
        
        # For recurring bookings, create the parent booking first
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        parent_booking = serializer.save()
        
        # Generate recurring instances
        self.generate_recurring_instances(parent_booking)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def generate_recurring_instances(self, parent_booking):
        """Generate future booking instances based on recurrence rule"""
        from datetime import timedelta, datetime
        from dateutil.relativedelta import relativedelta
        
        if parent_booking.recurrence_rule == 'N' or not parent_booking.recurrence_end_date:
            return
        
        current_date = parent_booking.scheduled_time
        end_date = parent_booking.recurrence_end_date
        
        # Define the increment based on recurrence rule
        if parent_booking.recurrence_rule == 'D':  # Daily
            delta = timedelta(days=1)
        elif parent_booking.recurrence_rule == 'W':  # Weekly
            delta = timedelta(weeks=1)
        elif parent_booking.recurrence_rule == 'M':  # Monthly
            delta = relativedelta(months=1)
        elif parent_booking.recurrence_rule == 'Y':  # Yearly
            delta = relativedelta(years=1)
        else:
            return
        
        # Generate instances until end date
        current_date += delta  # Start from next occurrence
        while current_date <= end_date:
            # Check if the service provider is available on this date
            day_str = current_date.strftime('%Y-%m-%d')
            if day_str in parent_booking.service_provider.availability:
                # Check if there are already enough bookings for this slot
                existing_bookings = Booking.objects.filter(
                    service_provider=parent_booking.service_provider,
                    scheduled_time=current_date
                ).count()
                
                if existing_bookings < parent_booking.service_provider.max_booking_per_slot:
                    # Create a new booking instance
                    new_booking = Booking.objects.create(
                        user=parent_booking.user,
                        service_provider=parent_booking.service_provider,
                        service_type=parent_booking.service_type,
                        scheduled_time=current_date,
                        duration=parent_booking.duration,
                        status='P',  # Pending by default
                        price=parent_booking.price,  # This will be recalculated in save()
                        parent_booking=parent_booking,
                        is_recurring_instance=True,
                        recurrence_rule='N'  # Instances don't recur themselves
                    )
            
            # Move to next occurrence
            current_date += delta

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

class LoyaltyProgramViewSet(viewsets.ModelViewSet):
    queryset = LoyaltyProgram.objects.all()
    serializer_class = LoyaltyProgramSerializer
    permission_classes = [permissions.IsAuthenticated]

class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserMembershipViewSet(viewsets.ModelViewSet):
    queryset = UserMembership.objects.all()
    serializer_class = UserMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from decimal import Decimal
        amount = request.data.get('amount')
        booking_id = request.data.get('booking_id')
        order_id = request.data.get('order_id')

        base_amount = Decimal(str(amount))
        taxable_amount = base_amount * Decimal('0.9')
        gst = taxable_amount * Decimal('0.18')
        total_amount = int((taxable_amount + gst) * 100)  # Razorpay accepts amount in paisa

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        payment_data = {
            'amount': total_amount,
            'currency': 'INR',
            'receipt': f'receipt_{datetime.now().timestamp()}',
            'payment_capture': 1
        }

        if booking_id:
            payment_data['notes'] = {'booking_id': booking_id}
        elif order_id:
            payment_data['notes'] = {'order_id': order_id}

        try:
            order = client.order.create(data=payment_data)
            Payment.objects.create(
                user=request.user,
                amount=total_amount,
                payment_method='Razorpay',
                transaction_id=order['id'],
                status='Pending'
            )
            return Response(order)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@csrf_exempt
def payment_callback(request):
    payload = request.data
    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        client.utility.verify_payment_signature(payload)

        payment = Payment.objects.get(transaction_id=payload['razorpay_order_id'])
        payment.status = 'Completed' if payload.get('razorpay_payment_id') else 'Failed'
        payment.save()

        if payment.status == 'Completed':
            # Update loyalty points (1 point per 100 INR spent)
            loyalty, _ = LoyaltyProgram.objects.get_or_create(user=payment.user)
            points_earned = int(payment.amount / 10000)  # Convert paisa to points
            loyalty.points += points_earned
            
            # Update tier based on total points
            if loyalty.points >= 1000:
                loyalty.tier = 'G'  # Gold
            elif loyalty.points >= 500:
                loyalty.tier = 'S'  # Silver
            loyalty.save()

            # Create notification for points earned
            Notification.objects.create(
                user=payment.user,
                message=f'You earned {points_earned} loyalty points from your recent transaction!',
                notification_type='loyalty',
                status='Unread'
            )

            # Update related booking/order status
            if payment.booking:
                payment.booking.status = 'C'  # Confirmed
                payment.booking.save()
            elif payment.order:
                payment.order.status = 'S'  # Shipped
                payment.order.save()

        # Update loyalty points (1 point per ₹100 spent)
        if payment.status == 'Completed':
            points = int(payment.amount // 100)
            loyalty, _ = LoyaltyProgram.objects.get_or_create(user=payment.user)
            loyalty.points += points
            
            # Update tier based on accumulated points
            if loyalty.points >= 1000:
                loyalty.tier = 'G'
            elif loyalty.points >= 500:
                loyalty.tier = 'S'
            loyalty.save()

        return Response({'status': 'Payment successful'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Apply membership discount
        if request.user.membership_status == 'P':
            amount = float(amount) * 0.9  # 10% discount for premium members

        # Calculate GST (18% on 90% of amount as per Indian regulations)
        taxable_amount = float(amount) * 0.9
        gst = taxable_amount * 0.18
        total_amount = int((taxable_amount + gst) * 100)
