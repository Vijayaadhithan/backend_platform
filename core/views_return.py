from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import ReturnRequest, Order, Payment
from .serializers import ReturnRequestSerializer
import razorpay
from django.conf import settings

class ReturnRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing return requests.
    Provides CRUD functionality for ReturnRequest model with additional actions for processing refunds.
    """
    queryset = ReturnRequest.objects.all()
    serializer_class = ReturnRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter return requests based on user permissions:
        - Staff users can see all return requests
        - Regular users can only see their own return requests
        """
        user = self.request.user
        if user.is_staff:
            return ReturnRequest.objects.all()
        
        # Regular users can only see their own return requests
        return ReturnRequest.objects.filter(user=user)
    
    def perform_create(self, serializer):
        """
        Set the user of the return request to the current user when creating a new return request.
        """
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a return request and initiate the refund process.
        Only staff users can approve return requests.
        """
        if not request.user.is_staff:
            return Response({"error": "Only staff users can approve return requests"}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        return_request = self.get_object()
        
        # Check if the return request is already approved or completed
        if return_request.status in ['A', 'C']:
            return Response({"error": "This return request has already been approved or completed"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate refund amount if not already set
        if not return_request.refund_amount:
            # Sum the prices of the items being returned
            refund_amount = sum(item.price * item.quantity for item in return_request.items.all())
            return_request.refund_amount = refund_amount
        
        # Update status to approved
        return_request.status = 'A'
        return_request.admin_notes = request.data.get('admin_notes', '')
        return_request.save()
        
        # Process the refund through Razorpay
        success = return_request.process_refund()
        
        if success:
            return Response({"message": "Return request approved and refund processed successfully"})
        else:
            return Response({"message": "Return request approved but refund processing failed. Check admin notes for details."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject a return request.
        Only staff users can reject return requests.
        """
        if not request.user.is_staff:
            return Response({"error": "Only staff users can reject return requests"}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        return_request = self.get_object()
        
        # Check if the return request is already approved, rejected or completed
        if return_request.status in ['A', 'R', 'C']:
            return Response({"error": "This return request has already been processed"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Update status to rejected
        return_request.status = 'R'
        return_request.admin_notes = request.data.get('admin_notes', '')
        return_request.save()
        
        return Response({"message": "Return request rejected successfully"})
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        Get all pending return requests.
        Only staff users can access this endpoint.
        """
        if not request.user.is_staff:
            return Response({"error": "Only staff users can view pending return requests"}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        pending_requests = ReturnRequest.objects.filter(status='P')
        serializer = self.get_serializer(pending_requests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_returns(self, request):
        """
        Get all return requests for the current user.
        """
        user_returns = ReturnRequest.objects.filter(user=request.user)
        serializer = self.get_serializer(user_returns, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def refund_status(self, request, pk=None):
        """
        Check the status of a refund for a return request.
        """
        return_request = self.get_object()
        
        # If no refund has been initiated, return appropriate message
        if not return_request.refund_id:
            return Response({"status": "No refund has been initiated for this return request"})
        
        # If refund has been initiated, check its status in Razorpay
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            refund = client.refund.fetch(return_request.refund_id)
            
            return Response({
                "refund_id": return_request.refund_id,
                "status": refund.get('status', 'Unknown'),
                "amount": float(return_request.refund_amount),
                "created_at": refund.get('created_at', 'Unknown')
            })
        except Exception as e:
            return Response({"error": f"Failed to fetch refund status: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)