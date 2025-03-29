from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email_notification(to_email, subject, content):
    """
    Send email notifications using SendGrid.
    """
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        message = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=content
        )
        sg.send(message)
        return True
    except Exception as e:
        print(f'SendGrid Error: {str(e)}')
        return False

def send_booking_confirmation(booking):
    """
    Send booking confirmation email.
    """
    subject = 'Booking Confirmation'
    content = f'''
    <h2>Booking Confirmed!</h2>
    <p>Dear {booking.user.username},</p>
    <p>Your booking has been confirmed with the following details:</p>
    <ul>
        <li>Service: {booking.service_type.name}</li>
        <li>Provider: {booking.service_provider.name}</li>
        <li>Date: {booking.scheduled_time}</li>
        <li>Price: ₹{booking.price}</li>
    </ul>
    '''
    return send_email_notification(booking.user.email, subject, content)

def send_order_confirmation(order):
    """
    Send order confirmation email.
    """
    items_list = ''.join([f'<li>{item.product.name} x {item.quantity}: ₹{item.price}</li>' 
                         for item in order.items.all()])
    subject = 'Order Confirmation'
    content = f'''
    <h2>Order Confirmed!</h2>
    <p>Dear {order.user.username},</p>
    <p>Your order has been confirmed with the following details:</p>
    <ul>
        {items_list}
    </ul>
    <p>Total Amount: ₹{order.total_price}</p>
    '''
    return send_email_notification(order.user.email, subject, content)

def send_payment_confirmation(payment):
    """
    Send payment confirmation email.
    """
    subject = 'Payment Confirmation'
    content = f'''
    <h2>Payment Successful!</h2>
    <p>Dear {payment.user.username},</p>
    <p>Your payment of ₹{payment.amount/100:.2f} has been processed successfully.</p>
    <p>Transaction ID: {payment.transaction_id}</p>
    '''
    return send_email_notification(payment.user.email, subject, content)

def send_membership_confirmation(user_membership):
    """
    Send membership confirmation email.
    """
    subject = 'Membership Confirmation'
    content = f'''
    <h2>Welcome to {user_membership.membership.name} Membership!</h2>
    <p>Dear {user_membership.user.username},</p>
    <p>Your membership has been activated with the following details:</p>
    <ul>
        <li>Membership Type: {user_membership.membership.name}</li>
        <li>Start Date: {user_membership.start_date}</li>
        <li>End Date: {user_membership.end_date}</li>
    </ul>
    <p>Enjoy your premium benefits!</p>
    '''
    return send_email_notification(user_membership.user.email, subject, content)