# API Documentation

This document provides comprehensive information about the API endpoints available in the application. Frontend developers can use this as a reference to understand how to interact with the backend services.

## Base URL

All API endpoints are prefixed with `/api/`

## Authentication

### JWT Authentication

```
POST /api/token/
POST /api/token/refresh/
```

#### Request Body (POST /api/token/)

```json
{
  "username": "user@example.com",
  "password": "yourpassword"
}
```

#### Response

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Request Body (POST /api/token/refresh/)

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Session Authentication

```
POST /api/login/
POST /api/logout/
```

#### Request Body (POST /api/login/)

```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

#### Response

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "membership_status": "F"
  },
  "message": "Login successful"
}
```

### Token Authentication

```
POST /api/register/
POST /api/token/
```

#### Request Body (POST /api/register/)

```json
{
  "email": "user@example.com",
  "password": "yourpassword",
  "username": "username"
}
```

#### Response

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username"
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

#### Request Body (POST /api/token/)

```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

#### Response

```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 1,
  "membership_status": "F"
}
```

### Password Reset

```
POST /api/password-reset/
POST /api/password-reset-confirm/
```

#### Request Body (POST /api/password-reset/)

```json
{
  "email": "user@example.com"
}
```

#### Response

```json
{
  "message": "Password reset email sent"
}
```

#### Request Body (POST /api/password-reset-confirm/)

```json
{
  "uid": "MQ",
  "token": "5jz-a9b1f1d4e63db7b8c84e",
  "new_password": "newpassword"
}
```

#### Response

```json
{
  "message": "Password reset successful"
}
```

### Language Preference

```
POST /api/change-language/
```

#### Request Body

```json
{
  "language_code": "en"
}
```

#### Response

```json
{
  "message": "Language preference updated successfully"
}
```

## Users

### List Users

```
GET /api/users/
```

#### Response

```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "membership_status": "F",
    "language_preference": "en"
  }
]
```

### Get User

```
GET /api/users/{id}/
```

#### Response

```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "membership_status": "F",
  "language_preference": "en"
}
```

### Update User

```
PUT /api/users/{id}/
PATCH /api/users/{id}/
```

#### Request Body

```json
{
  "username": "newusername",
  "language_preference": "de"
}
```

#### Response

```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "newusername",
  "membership_status": "F",
  "language_preference": "de"
}
```

## Service Providers

### List Service Providers

```
GET /api/service-providers/
```

#### Response

```json
[
  {
    "id": 1,
    "name": "Provider Name",
    "description": "Provider description",
    "service_types": [1, 2],
    "rating": 4.5,
    "is_available": true
  }
]
```

### Get Service Provider

```
GET /api/service-providers/{id}/
```

#### Response

```json
{
  "id": 1,
  "name": "Provider Name",
  "description": "Provider description",
  "service_types": [1, 2],
  "rating": 4.5,
  "is_available": true
}
```

### Create Service Provider

```
POST /api/service-providers/
```

#### Request Body

```json
{
  "name": "New Provider",
  "description": "Provider description",
  "service_types": [1, 2],
  "is_available": true
}
```

## Service Types

### List Service Types

```
GET /api/service-types/
```

#### Response

```json
[
  {
    "id": 1,
    "name": "Service Type Name",
    "description": "Service type description",
    "base_price": 100.00
  }
]
```

## Products

### List Products

```
GET /api/products/
```

#### Query Parameters

- `category`: Filter by category
- `min_price`: Filter by minimum price
- `max_price`: Filter by maximum price
- `search`: Search in name and description

#### Response

```json
[
  {
    "id": 1,
    "name": "Product Name",
    "description": "Product description",
    "price": 50.00,
    "category": "Category",
    "in_stock": true,
    "images": ["url1", "url2"]
  }
]
```

### Get Product

```
GET /api/products/{id}/
```

#### Response

```json
{
  "id": 1,
  "name": "Product Name",
  "description": "Product description",
  "price": 50.00,
  "category": "Category",
  "in_stock": true,
  "images": ["url1", "url2"]
}
```

### Create Product

```
POST /api/products/
```

#### Request Body

```json
{
  "name": "New Product",
  "description": "Product description",
  "price": 50.00,
  "category": "Category",
  "in_stock": true,
  "images": ["url1", "url2"]
}
```

## Bookings

### List Bookings

```
GET /api/bookings/
```

#### Query Parameters

- `status`: Filter by status (P, C, X)
- `service_provider`: Filter by service provider ID
- `service_type`: Filter by service type ID
- `start_date`: Filter by start date
- `end_date`: Filter by end date

#### Response

```json
[
  {
    "id": 1,
    "user": 1,
    "service_provider": 1,
    "service_type": 1,
    "scheduled_time": "2023-06-15T14:00:00Z",
    "status": "P",
    "price": 100.00,
    "notes": "Booking notes",
    "created_at": "2023-06-10T10:00:00Z",
    "updated_at": "2023-06-10T10:00:00Z"
  }
]
```

### Get Booking

```
GET /api/bookings/{id}/
```

#### Response

```json
{
  "id": 1,
  "user": 1,
  "service_provider": 1,
  "service_type": 1,
  "scheduled_time": "2023-06-15T14:00:00Z",
  "status": "P",
  "price": 100.00,
  "notes": "Booking notes",
  "created_at": "2023-06-10T10:00:00Z",
  "updated_at": "2023-06-10T10:00:00Z"
}
```

### Create Booking

```
POST /api/bookings/
```

#### Request Body

```json
{
  "service_provider": 1,
  "service_type": 1,
  "scheduled_time": "2023-06-15T14:00:00Z",
  "notes": "Booking notes"
}
```

### Cancel Booking

```
POST /api/bookings/{id}/cancel/
```

#### Request Body

```json
{
  "cancellation_reason": "Reason for cancellation"
}
```

## Orders

### List Orders

```
GET /api/orders/
```

#### Query Parameters

- `status`: Filter by status (P, C, X)
- `start_date`: Filter by start date
- `end_date`: Filter by end date

#### Response

```json
[
  {
    "id": 1,
    "user": 1,
    "items": [
      {
        "product": 1,
        "quantity": 2,
        "price": 100.00
      }
    ],
    "total_price": 100.00,
    "status": "P",
    "shipping_address": "Shipping address",
    "created_at": "2023-06-10T10:00:00Z",
    "updated_at": "2023-06-10T10:00:00Z"
  }
]
```

### Get Order

```
GET /api/orders/{id}/
```

#### Response

```json
{
  "id": 1,
  "user": 1,
  "items": [
    {
      "product": 1,
      "quantity": 2,
      "price": 100.00
    }
  ],
  "total_price": 100.00,
  "status": "P",
  "shipping_address": "Shipping address",
  "created_at": "2023-06-10T10:00:00Z",
  "updated_at": "2023-06-10T10:00:00Z"
}
```

### Create Order

```
POST /api/orders/
```

#### Request Body

```json
{
  "items": [
    {
      "product": 1,
      "quantity": 2
    }
  ],
  "shipping_address": "Shipping address"
}
```

### Cancel Order

```
POST /api/orders/{id}/cancel/
```

## Payments

### Create Payment

```
POST /api/payment/
```

#### Request Body

```json
{
  "amount": 100.00,
  "booking_id": 1,
  "order_id": null
}
```

#### Response

```json
{
  "order_id": "order_JDvKaVNGgZt7Ey",
  "amount": 10620,
  "currency": "INR",
  "key": "rzp_test_yourkeyhere"
}
```

### Payment Callback

```
POST /api/payment-callback/
```

#### Request Body

```json
{
  "razorpay_payment_id": "pay_JDvKbVNGgZt7Ey",
  "razorpay_order_id": "order_JDvKaVNGgZt7Ey",
  "razorpay_signature": "signature"
}
```

## Loyalty Programs

### List Loyalty Programs

```
GET /api/loyalty/
```

#### Response

```json
[
  {
    "id": 1,
    "name": "Loyalty Program Name",
    "description": "Loyalty program description",
    "points_per_purchase": 10,
    "points_value": 0.01
  }
]
```

## Memberships

### List Memberships

```
GET /api/memberships/
```

#### Response

```json
[
  {
    "id": 1,
    "name": "Membership Name",
    "description": "Membership description",
    "price": 100.00,
    "duration_days": 30,
    "benefits": "Membership benefits"
  }
]
```

### Get User Memberships

```
GET /api/user-memberships/
```

#### Response

```json
[
  {
    "id": 1,
    "user": 1,
    "membership": 1,
    "start_date": "2023-06-10",
    "end_date": "2023-07-10",
    "is_active": true
  }
]
```

### Purchase Membership

```
POST /api/user-memberships/
```

#### Request Body

```json
{
  "membership": 1
}
```

## Reviews

### List Reviews

```
GET /api/reviews/
```

#### Query Parameters

- `service_provider`: Filter by service provider ID
- `product`: Filter by product ID
- `min_rating`: Filter by minimum rating
- `max_rating`: Filter by maximum rating

#### Response

```json
[
  {
    "id": 1,
    "user": 1,
    "service_provider": 1,
    "product": null,
    "rating": 4,
    "comment": "Review comment",
    "created_at": "2023-06-10T10:00:00Z"
  }
]
```

### Create Review

```
POST /api/reviews/
```

#### Request Body

```json
{
  "service_provider": 1,
  "product": null,
  "rating": 4,
  "comment": "Review comment"
}
```

## Notifications

### List Notifications

```
GET /api/notifications/
```

#### Response

```json
[
  {
    "id": 1,
    "user": 1,
    "title": "Notification Title",
    "message": "Notification message",
    "is_read": false,
    "created_at": "2023-06-10T10:00:00Z"
  }
]
```

### Mark Notification as Read

```
PATCH /api/notifications/{id}/
```

#### Request Body

```json
{
  "is_read": true
}
```

## Shops

### List Shops

```
GET /api/shops/
```

#### Response

```json
[
  {
    "id": 1,
    "name": "Shop Name",
    "description": "Shop description",
    "owner": 1,
    "logo": "logo_url",
    "address": "Shop address",
    "contact_email": "shop@example.com",
    "contact_phone": "+1234567890",
    "is_active": true,
    "created_at": "2023-06-10T10:00:00Z",
    "updated_at": "2023-06-10T10:00:00Z"
  }
]
```

### Get Shop

```
GET /api/shops/{id}/
```

#### Response

```json
{
  "id": 1,
  "name": "Shop Name",
  "description": "Shop description",
  "owner": 1,
  "logo": "logo_url",
  "address": "Shop address",
  "contact_email": "shop@example.com",
  "contact_phone": "+1234567890",
  "is_active": true,
  "created_at": "2023-06-10T10:00:00Z",
  "updated_at": "2023-06-10T10:00:00Z"
}
```

### Create Shop

```
POST /api/shops/
```

#### Request Body

```json
{
  "name": "New Shop",
  "description": "Shop description",
  "logo": "logo_url",
  "address": "Shop address",
  "contact_email": "shop@example.com",
  "contact_phone": "+1234567890"
}
```

## Return Requests

### List Return Requests

```
GET /api/return-requests/
```

#### Response

```json
[
  {
    "id": 1,
    "user": 1,
    "order": 1,
    "items": [
      {
        "product": 1,
        "quantity": 1,
        "price": 50.00,
        "reason": "Return reason"
      }
    ],
    "status": "P",
    "refund_amount": 50.00,
    "admin_notes": "Admin notes",
    "created_at": "2023-06-10T10:00:00Z",
    "updated_at": "2023-06-10T10:00:00Z"
  }
]
```

### Create Return Request

```
POST /api/return-requests/
```

#### Request Body

```json
{
  "order": 1,
  "items": [
    {
      "product": 1,
      "quantity": 1,
      "reason": "Return reason"
    }
  ]
}
```

### Approve Return Request (Staff Only)

```
POST /api/return-requests/{id}/approve/
```

#### Request Body

```json
{
  "admin_notes": "Approval notes"
}
```

### Reject Return Request (Staff Only)

```
POST /api/return-requests/{id}/reject/
```

#### Request Body

```json
{
  "admin_notes": "Rejection reason"
}
```

## Coupons

### List Coupons

```
GET /api/coupons/
```

#### Query Parameters

- `is_active`: Filter by active status
- `code`: Filter by coupon code
- `min_discount`: Filter by minimum discount amount
- `max_discount`: Filter by maximum discount amount
- `valid_from`: Filter by valid from date
- `valid_until`: Filter by valid until date

#### Response

```json
[
  {
    "id": 1,
    "code": "SUMMER10",
    "discount_type": "P",
    "discount_amount": 10.00,
    "min_purchase_amount": 100.00,
    "valid_from": "2023-06-01T00:00:00Z",
    "valid_until": "2023-08-31T23:59:59Z",
    "max_uses": 100,
    "max_uses_per_user": 1,
    "is_active": true,
    "created_at": "2023-06-01T00:00:00Z"
  }
]
```

### Apply Coupon

```
POST /api/coupons/{id}/apply/
```

#### Request Body

```json
{
  "products": [1, 2],
  "categories": ["Category1"],
  "shop_id": 1,
  "total_amount": 150.00
}
```

#### Response

```json
{
  "valid": true,
  "discount": 15.00,
  "final_amount": 135.00
}
```

### Redeem Coupon

```
POST /api/coupons/{id}/redeem/
```

#### Request Body

```json
{
  "order_id": 1,
  "booking_id": null,
  "amount": 150.00
}
```

### List Coupon Usages

```
GET /api/coupon-usages/
```

#### Response

```json
[
  {
    "id": 1,
    "coupon": 1,
    "user": 1,
    "order": 1,
    "booking": null,
    "discount_amount": 15.00,
    "used_at": "2023-06-10T10:00:00Z"
  }
]
```

## Analytics (Staff Only)

### Get Analytics Data

```
GET /api/analytics/
```

#### Query Parameters

- `period`: Time period for analytics (daily, weekly, monthly, yearly)
- `start_date`: Start date for analytics (YYYY-MM-DD)
- `end_date`: End date for analytics (YYYY-MM-DD)
- `metrics`: Comma-separated list of metrics to include (sales, bookings, users, products, services, returns)

#### Response

```json
{
  "sales": {
    "total_revenue": 5000.00,
    "average_order_value": 100.00,
    "order_count": 50,
    "time_series": [
      {
        "period": "2023-06-01",
        "revenue": 1000.00,
        "order_count": 10
      }
    ]
  },
  "bookings": {
    "total_bookings": 30,
    "completed_bookings": 25,
    "cancelled_bookings": 5,
    "time_series": [
      {
        "period": "2023-06-01",
        "booking_count": 5,
        "completed_count": 4,
        "cancelled_count": 1
      }
    ]
  },
  "users": {
    "total_users": 100,
    "new_users": 20,
    "premium_users": 15,
    "time_series": [
      {
        "period": "2023-06-01",
        "new_users": 5
      }
    ]
  }
}
```

## Status Codes

- `200 OK`: The request was successful
- `201 Created`: The resource was successfully created
- `400 Bad Request`: The request was invalid or cannot be served
- `401 Unauthorized`: Authentication failed or user doesn't have permissions
- `403 Forbidden`: The user is authenticated but doesn't have permission
- `404 Not Found`: The requested resource could not be found
- `500 Internal Server Error`: An error occurred on the server

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message",
  "detail": "Detailed error description"
}
```

or for validation errors:

```json
{
  "field_name": [
    "Error message for this field"
  ]
}
```