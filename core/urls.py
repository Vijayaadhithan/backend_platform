from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import auth_views
from . import views_shop
from . import views_return
from . import views_analytics

router = DefaultRouter()
router.register('users', views.UserViewSet)
router.register('service-providers', views.ServiceProviderViewSet)
router.register('service-types', views.ServiceTypeViewSet)
router.register('products', views.ProductViewSet)
router.register('bookings', views.BookingViewSet)
router.register('orders', views.OrderViewSet)
router.register('loyalty', views.LoyaltyProgramViewSet)
router.register('memberships', views.MembershipViewSet)
router.register('user-memberships', views.UserMembershipViewSet)
router.register('reviews', views.ReviewViewSet)
router.register('notifications', views.NotificationViewSet)
router.register('shops', views_shop.ShopViewSet)
router.register('return-requests', views_return.ReturnRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.CreateUserView.as_view(), name='register'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('payment/', views.PaymentView.as_view(), name='payment'),
    path('payment-callback/', views.payment_callback, name='payment-callback'),
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-reset/', auth_views.PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/', auth_views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('change-language/', auth_views.ChangeLanguageView.as_view(), name='change-language'),
    # Analytics URL
    path('analytics/', views_analytics.AnalyticsView.as_view(), name='analytics'),
]