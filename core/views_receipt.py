from rest_framework import permissions, status
from .security import get_permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Order, Booking, Payment
from .receipt_generator import ReceiptGenerator
import io

class GenerateReceiptView(APIView):
    permission_classes = get_permission_classes()
    
    def post(self, request):
        """Generate a PDF receipt for an order or booking"""
        order_id = request.data.get('order_id')
        booking_id = request.data.get('booking_id')
        
        if not order_id and not booking_id:
            return Response({
                'detail': 'Either order_id or booking_id must be provided.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Initialize receipt generator
        receipt_generator = ReceiptGenerator()
        
        # Generate receipt based on type
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                
                # Check if user is authorized to access this order
                if order.user != request.user and not request.user.is_staff:
                    return Response({
                        'detail': 'You do not have permission to access this order.'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # Get the payment for this order
                payment = Payment.objects.filter(order_id=order_id).first()
                
                # Generate the receipt
                buffer = io.BytesIO()
                receipt_generator.generate_order_receipt(order, payment, buffer)
                buffer.seek(0)
                
                # Return the PDF as a response
                response = HttpResponse(buffer, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="order_receipt_{order_id}.pdf"'
                return response
                
            except Order.DoesNotExist:
                return Response({
                    'detail': 'Order not found.'
                }, status=status.HTTP_404_NOT_FOUND)
        
        elif booking_id:
            try:
                booking = Booking.objects.get(id=booking_id)
                
                # Check if user is authorized to access this booking
                if booking.user != request.user and not request.user.is_staff:
                    return Response({
                        'detail': 'You do not have permission to access this booking.'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # Get the payment for this booking
                payment = Payment.objects.filter(booking_id=booking_id).first()
                
                # Generate the receipt
                buffer = io.BytesIO()
                receipt_generator.generate_booking_receipt(booking, payment, buffer)
                buffer.seek(0)
                
                # Return the PDF as a response
                response = HttpResponse(buffer, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="booking_receipt_{booking_id}.pdf"'
                return response
                
            except Booking.DoesNotExist:
                return Response({
                    'detail': 'Booking not found.'
                }, status=status.HTTP_404_NOT_FOUND)