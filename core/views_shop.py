from rest_framework import viewsets, permissions
from django.db.models import Q
from .models import Shop
from .serializers import ShopSerializer
from .security import get_permission_classes

class ShopViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing shop operations.
    Provides CRUD functionality for Shop model.
    """
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = get_permission_classes()
    
    def perform_create(self, serializer):
        """
        Set the owner of the shop to the current user when creating a new shop.
        """
        serializer.save(owner=self.request.user)
    
    def get_queryset(self):
        """
        Filter shops based on user permissions:
        - Staff users can see all shops
        - Regular users can only see active shops and their own shops
        """
        user = self.request.user
        if user.is_staff:
            return Shop.objects.all()
        
        # Regular users can see active shops and their own shops
        return Shop.objects.filter(
            Q(is_active=True) | Q(owner=user)
        )