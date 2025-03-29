from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters import rest_framework as filters
from .models import Coupon, CouponUsage
from .serializers import CouponSerializer, CouponUsageSerializer
from .security import get_permission_classes

class CouponFilter(filters.FilterSet):
    is_active = filters.BooleanFilter(field_name='is_active')
    code = filters.CharFilter(field_name='code', lookup_expr='icontains')
    min_discount = filters.NumberFilter(field_name='discount_amount', lookup_expr='gte')
    max_discount = filters.NumberFilter(field_name='discount_amount', lookup_expr='lte')
    valid_from = filters.DateFilter(field_name='valid_from', lookup_expr='gte')
    valid_until = filters.DateFilter(field_name='valid_until', lookup_expr='lte')
    
    class Meta:
        model = Coupon
        fields = ['is_active', 'code', 'discount_type', 'min_discount', 'max_discount', 'valid_from', 'valid_until']

class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = get_permission_classes()
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = CouponFilter
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """Apply a coupon to check if it's valid for the current context"""
        coupon = self.get_object()
        
        # Get context from request data
        products = request.data.get('products', [])
        categories = request.data.get('categories', [])
        shop_id = request.data.get('shop_id')
        total_amount = request.data.get('total_amount', 0)
        
        # Check if coupon is valid
        if not coupon.is_active:
            return Response({'detail': 'This coupon is not active.'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Check if coupon is expired
        from django.utils import timezone
        now = timezone.now()
        if coupon.valid_from and coupon.valid_from > now:
            return Response({'detail': 'This coupon is not yet valid.'}, status=status.HTTP_400_BAD_REQUEST)
        if coupon.valid_until and coupon.valid_until < now:
            return Response({'detail': 'This coupon has expired.'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Check if user has already used this coupon
        if coupon.max_uses_per_user > 0:
            user_usage_count = CouponUsage.objects.filter(coupon=coupon, user=request.user).count()
            if user_usage_count >= coupon.max_uses_per_user:
                return Response({'detail': 'You have already used this coupon the maximum number of times.'}, 
                                status=status.HTTP_400_BAD_REQUEST)
        
        # Check minimum purchase amount
        if coupon.min_purchase_amount and float(total_amount) < coupon.min_purchase_amount:
            return Response({
                'detail': f'Minimum purchase amount of {coupon.min_purchase_amount} required for this coupon.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate discount
        discount = coupon.calculate_discount(float(total_amount))
        
        return Response({
            'valid': True,
            'discount': discount,
            'final_amount': float(total_amount) - discount
        })
    
    @action(detail=True, methods=['post'])
    def redeem(self, request, pk=None):
        """Redeem a coupon and create usage record"""
        coupon = self.get_object()
        order_id = request.data.get('order_id')
        booking_id = request.data.get('booking_id')
        amount = request.data.get('amount', 0)
        
        # Validate the coupon first
        if not coupon.is_active:
            return Response({'detail': 'This coupon is not active.'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Create usage record
        usage = CouponUsage.objects.create(
            coupon=coupon,
            user=request.user,
            order_id=order_id,
            booking_id=booking_id,
            discount_amount=coupon.calculate_discount(float(amount))
        )
        
        return Response(CouponUsageSerializer(usage).data, status=status.HTTP_201_CREATED)

class CouponUsageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CouponUsageSerializer
    permission_classes = get_permission_classes()
    
    def get_queryset(self):
        # Regular users can only see their own coupon usages
        if not self.request.user.is_staff:
            return CouponUsage.objects.filter(user=self.request.user)
        # Staff can see all coupon usages
        return CouponUsage.objects.all()