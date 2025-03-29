# Full Stack Service Application

A comprehensive full-stack application for service booking and product ordering with multi-language support, payment integration, and analytics.

## Features

- **User Authentication**: Secure registration, login, and profile management
- **Service Booking**: Schedule and manage service appointments
- **Product Ordering**: Browse and purchase products
- **Multi-language Support**: Available in English, Tamil, and Hindi
- **Payment Integration**: Secure payments via Razorpay
- **Loyalty Program**: Reward system for regular customers
- **Analytics Dashboard**: Track sales, bookings, and customer metrics
- **Receipt Generation**: PDF receipts for orders and bookings
- **Return Management**: Process and track return requests
- **Shop Management**: Multi-shop support with individual configurations

## Technology Stack

- **Backend**: Django with Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **PDF Generation**: ReportLab
- **Payment Gateway**: Razorpay
- **Internationalization**: django-modeltranslation

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd full_stack_app
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Copy `.env.example` to `.env` (if not already present)
   - Update the values in `.env` with your configuration

5. Set up the database:
   ```
   python manage.py migrate
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

## Environment Variables

The application uses the following environment variables (configured in `.env`):

- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DATABASE_URL`: PostgreSQL connection string
- `RAZORPAY_KEY_ID`: Razorpay API key ID
- `RAZORPAY_KEY_SECRET`: Razorpay API key secret
- `SENDGRID_API_KEY`: SendGrid API key for email
- `DEFAULT_FROM_EMAIL`: Default sender email address

## API Documentation

The API endpoints are organized as follows:

- `/api/auth/`: Authentication endpoints
- `/api/users/`: User management
- `/api/services/`: Service booking
- `/api/products/`: Product catalog and ordering
- `/api/bookings/`: Booking management
- `/api/orders/`: Order management
- `/api/payments/`: Payment processing
- `/api/returns/`: Return request handling
- `/api/analytics/`: Business analytics

## Internationalization

The application supports multiple languages:

- English (default)
- Tamil
- Hindi

To generate or update translation files:

```
python manage.py makemessages -l ta -l hi
python manage.py compilemessages
```

## License

[MIT License](LICENSE)