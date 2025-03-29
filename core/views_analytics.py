from rest_framework import views, permissions, status
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg, F, ExpressionWrapper, fields
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.utils import timezone
from datetime import timedelta
from .models import Order, Booking, User, Product, ServiceProvider, Payment, ReturnRequest

class AnalyticsView(views.APIView):
    """
    API view for providing analytics data for the dashboard.
    Only accessible to staff users.
    """
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        """
        Get analytics data based on the requested time period and metrics.
        
        Query parameters:
        - period: The time period for the analytics (daily, weekly, monthly, yearly)
        - start_date: The start date for the analytics (YYYY-MM-DD)
        - end_date: The end date for the analytics (YYYY-MM-DD)
        - metrics: Comma-separated list of metrics to include (sales, bookings, users, etc.)
        """
        period = request.query_params.get('period', 'monthly')
        metrics = request.query_params.get('metrics', 'all')
        
        # Parse date range
        try:
            start_date = request.query_params.get('start_date')
            if start_date:
                start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
            else:
                # Default to last 30 days if no start date provided
                start_date = (timezone.now() - timedelta(days=30)).date()
                
            end_date = request.query_params.get('end_date')
            if end_date:
                end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
            else:
                end_date = timezone.now().date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Convert dates to datetime with time component
        start_datetime = timezone.datetime.combine(start_date, timezone.datetime.min.time())
        end_datetime = timezone.datetime.combine(end_date, timezone.datetime.max.time())
        
        # Determine the truncation function based on the period
        if period == 'daily':
            trunc_func = TruncDay
        elif period == 'weekly':
            trunc_func = TruncWeek
        elif period == 'yearly':
            trunc_func = lambda field: timezone.datetime(field.year, 1, 1)
        else:  # Default to monthly
            trunc_func = TruncMonth
        
        # Initialize response data
        response_data = {}
        
        # Include all metrics by default, or parse the requested metrics
        requested_metrics = metrics.split(',') if metrics != 'all' else [
            'sales', 'bookings', 'users', 'products', 'services', 'returns'
        ]
        
        # Sales metrics
        if 'sales' in requested_metrics:
            sales_data = self._get_sales_metrics(start_datetime, end_datetime, trunc_func)
            response_data['sales'] = sales_data
        
        # Booking metrics
        if 'bookings' in requested_metrics:
            booking_data = self._get_booking_metrics(start_datetime, end_datetime, trunc_func)
            response_data['bookings'] = booking_data
        
        # User metrics
        if 'users' in requested_metrics:
            user_data = self._get_user_metrics(start_datetime, end_datetime, trunc_func)
            response_data['users'] = user_data
        
        # Product metrics
        if 'products' in requested_metrics:
            product_data = self._get_product_metrics(start_datetime, end_datetime)
            response_data['products'] = product_data
        
        # Service provider metrics
        if 'services' in requested_metrics:
            service_data = self._get_service_metrics(start_datetime, end_datetime)
            response_data['services'] = service_data
        
        # Return request metrics
        if 'returns' in requested_metrics:
            return_data = self._get_return_metrics(start_datetime, end_datetime, trunc_func)
            response_data['returns'] = return_data
        
        return Response(response_data)
    
    def _get_sales_metrics(self, start_date, end_date, trunc_func):
        """
        Get sales metrics for the specified period.
        """
        # Get orders created in the period
        orders = Order.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Total sales amount
        total_sales = orders.aggregate(total=Sum('total_price'))['total'] or 0
        
        # Sales by status
        sales_by_status = orders.values('status').annotate(
            count=Count('id'),
            total=Sum('total_price')
        )
        
        # Sales over time
        sales_over_time = orders.annotate(
            period=trunc_func('created_at')
        ).values('period').annotate(
            count=Count('id'),
            total=Sum('total_price')
        ).order_by('period')
        
        # Format the sales over time data
        formatted_sales_over_time = [
            {
                'period': entry['period'].strftime('%Y-%m-%d'),
                'count': entry['count'],
                'total': float(entry['total'])
            }
            for entry in sales_over_time
        ]
        
        # Get payment data
        payments = Payment.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            order__isnull=False
        )
        
        # Payments by method
        payments_by_method = payments.values('payment_method').annotate(
            count=Count('id'),
            total=Sum('amount')
        )
        
        return {
            'total_sales': float(total_sales),
            'order_count': orders.count(),
            'average_order_value': float(total_sales / orders.count()) if orders.count() > 0 else 0,
            'sales_by_status': [
                {
                    'status': status['status'],
                    'count': status['count'],
                    'total': float(status['total'])
                }
                for status in sales_by_status
            ],
            'sales_over_time': formatted_sales_over_time,
            'payments_by_method': [
                {
                    'method': method['payment_method'],
                    'count': method['count'],
                    'total': float(method['total'])
                }
                for method in payments_by_method
            ]
        }
    
    def _get_booking_metrics(self, start_date, end_date, trunc_func):
        """
        Get booking metrics for the specified period.
        """
        # Get bookings created in the period
        bookings = Booking.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Total bookings amount
        total_bookings_amount = bookings.aggregate(total=Sum('price'))['total'] or 0
        
        # Bookings by status
        bookings_by_status = bookings.values('status').annotate(
            count=Count('id'),
            total=Sum('price')
        )
        
        # Bookings over time
        bookings_over_time = bookings.annotate(
            period=trunc_func('created_at')
        ).values('period').annotate(
            count=Count('id'),
            total=Sum('price')
        ).order_by('period')
        
        # Format the bookings over time data
        formatted_bookings_over_time = [
            {
                'period': entry['period'].strftime('%Y-%m-%d'),
                'count': entry['count'],
                'total': float(entry['total'])
            }
            for entry in bookings_over_time
        ]
        
        # Bookings by service type
        bookings_by_service = bookings.values(
            'service_type__name'
        ).annotate(
            count=Count('id'),
            total=Sum('price')
        )
        
        # Recurring vs. one-time bookings
        recurring_bookings = bookings.filter(recurrence_rule__ne='N').count()
        one_time_bookings = bookings.filter(recurrence_rule='N').count()
        
        return {
            'total_bookings_amount': float(total_bookings_amount),
            'booking_count': bookings.count(),
            'average_booking_value': float(total_bookings_amount / bookings.count()) if bookings.count() > 0 else 0,
            'bookings_by_status': [
                {
                    'status': status['status'],
                    'count': status['count'],
                    'total': float(status['total'])
                }
                for status in bookings_by_status
            ],
            'bookings_over_time': formatted_bookings_over_time,
            'bookings_by_service': [
                {
                    'service_type': service['service_type__name'],
                    'count': service['count'],
                    'total': float(service['total'])
                }
                for service in bookings_by_service
            ],
            'recurring_vs_one_time': {
                'recurring': recurring_bookings,
                'one_time': one_time_bookings
            }
        }
    
    def _get_user_metrics(self, start_date, end_date, trunc_func):
        """
        Get user metrics for the specified period.
        """
        # Get users created in the period
        users = User.objects.filter(
            date_joined__gte=start_date,
            date_joined__lte=end_date
        )
        
        # Total users
        total_users = User.objects.count()
        
        # New users over time
        users_over_time = users.annotate(
            period=trunc_func('date_joined')
        ).values('period').annotate(
            count=Count('id')
        ).order_by('period')
        
        # Format the users over time data
        formatted_users_over_time = [
            {
                'period': entry['period'].strftime('%Y-%m-%d'),
                'count': entry['count']
            }
            for entry in users_over_time
        ]
        
        # Users by membership status
        users_by_membership = User.objects.values('membership_status').annotate(
            count=Count('id')
        )
        
        # Active users (made a booking or order in the last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        active_users_count = User.objects.filter(
            models.Q(booking__created_at__gte=thirty_days_ago) | 
            models.Q(order__created_at__gte=thirty_days_ago)
        ).distinct().count()
        
        return {
            'total_users': total_users,
            'new_users': users.count(),
            'active_users': active_users_count,
            'users_over_time': formatted_users_over_time,
            'users_by_membership': [
                {
                    'membership_status': membership['membership_status'],
                    'count': membership['count']
                }
                for membership in users_by_membership
            ]
        }
    
    def _get_product_metrics(self, start_date, end_date):
        """
        Get product metrics for the specified period.
        """
        # Get order items for orders in the period
        order_items = OrderItem.objects.filter(
            order__created_at__gte=start_date,
            order__created_at__lte=end_date
        )
        
        # Top selling products
        top_products = order_items.values(
            'product__id', 'product__name'
        ).annotate(
            quantity=Sum('quantity'),
            revenue=Sum(F('price') * F('quantity'))
        ).order_by('-quantity')[:10]
        
        # Products with low stock
        low_stock_products = Product.objects.filter(
            stock_quantity__lt=F('min_order_quantity') * 2
        ).values('id', 'name', 'stock_quantity', 'min_order_quantity')[:10]
        
        # Products by category
        products_by_category = Product.objects.values(
            'category__name'
        ).annotate(
            count=Count('id')
        )
        
        return {
            'top_selling_products': [
                {
                    'id': product['product__id'],
                    'name': product['product__name'],
                    'quantity_sold': product['quantity'],
                    'revenue': float(product['revenue'])
                }
                for product in top_products
            ],
            'low_stock_products': [
                {
                    'id': product['id'],
                    'name': product['name'],
                    'stock_quantity': product['stock_quantity'],
                    'min_order_quantity': product['min_order_quantity']
                }
                for product in low_stock_products
            ],
            'products_by_category': [
                {
                    'category': category['category__name'] or 'Uncategorized',
                    'count': category['count']
                }
                for category in products_by_category
            ]
        }
    
    def _get_service_metrics(self, start_date, end_date):
        """
        Get service provider metrics for the specified period.
        """
        # Get bookings for the period
        bookings = Booking.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Top service providers by bookings
        top_providers = bookings.values(
            'service_provider__id', 'service_provider__name'
        ).annotate(
            booking_count=Count('id'),
            revenue=Sum('price')
        ).order_by('-booking_count')[:10]
        
        # Service providers by rating
        providers_by_rating = ServiceProvider.objects.values(
            'id', 'name', 'rating', 'total_ratings'
        ).order_by('-rating')[:10]
        
        # Service providers by location
        providers_by_location = ServiceProvider.objects.values(
            'location'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        return {
            'top_service_providers': [
                {
                    'id': provider['service_provider__id'],
                    'name': provider['service_provider__name'],
                    'booking_count': provider['booking_count'],
                    'revenue': float(provider['revenue'])
                }
                for provider in top_providers
            ],
            'providers_by_rating': [
                {
                    'id': provider['id'],
                    'name': provider['name'],
                    'rating': float(provider['rating']),
                    'total_ratings': provider['total_ratings']
                }
                for provider in providers_by_rating
            ],
            'providers_by_location': [
                {
                    'location': location['location'],
                    'count': location['count']
                }
                for location in providers_by_location
            ]
        }
    
    def _get_return_metrics(self, start_date, end_date, trunc_func):
        """
        Get return request metrics for the specified period.
        """
        # Get return requests created in the period
        returns = ReturnRequest.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Total refund amount
        total_refund = returns.filter(status__in=['A', 'C']).aggregate(
            total=Sum('refund_amount')
        )['total'] or 0
        
        # Returns by status
        returns_by_status = returns.values('status').annotate(
            count=Count('id'),
            total=Sum('refund_amount', default=0)
        )
        
        # Returns over time
        returns_over_time = returns.annotate(
            period=trunc_func('created_at')
        ).values('period').annotate(
            count=Count('id'),
            total=Sum('refund_amount', default=0)
        ).order_by('period')
        
        # Format the returns over time data
        formatted_returns_over_time = [
            {
                'period': entry['period'].strftime('%Y-%m-%d'),
                'count': entry['count'],
                'total': float(entry['total'] or 0)
            }
            for entry in returns_over_time
        ]
        
        # Returns by reason
        returns_by_reason = returns.values('reason').annotate(
            count=Count('id'),
            total=Sum('refund_amount', default=0)
        )
        
        return {
            'total_returns': returns.count(),
            'total_refund_amount': float(total_refund),
            'returns_by_status': [
                {
                    'status': status['status'],
                    'count': status['count'],
                    'total': float(status['total'] or 0)
                }
                for status in returns_by_status
            ],
            'returns_over_time': formatted_returns_over_time,
            'returns_by_reason': [
                {
                    'reason': reason['reason'],
                    'count': reason['count'],
                    'total': float(reason['total'] or 0)
                }
                for reason in returns_by_reason
            ]
        }