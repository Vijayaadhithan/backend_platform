from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from django.conf import settings
import os
from decimal import Decimal
from datetime import datetime

class ReceiptGenerator:
    """
    Utility class for generating PDF receipts for orders and bookings.
    """
    
    @staticmethod
    def generate_order_receipt(order, payment):
        """
        Generate a PDF receipt for an order.
        
        Args:
            order: The Order object
            payment: The Payment object
            
        Returns:
            BytesIO: A buffer containing the PDF data
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Add company logo if available
        logo_path = os.path.join(settings.STATIC_ROOT, 'images/logo.png')
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=2*inch, height=1*inch)
            elements.append(logo)
        
        # Add title
        title_style = styles['Heading1']
        title = Paragraph("Order Receipt", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.25*inch))
        
        # Add order information
        order_info = [
            ["Order Number:", f"#{order.id}"],
            ["Date:", order.created_at.strftime("%Y-%m-%d %H:%M")],
            ["Customer:", f"{order.user.first_name} {order.user.last_name}"],
            ["Email:", order.user.email],
            ["Phone:", order.user.phone_number],
            ["Status:", order.get_status_display()]
        ]
        
        order_table = Table(order_info, colWidths=[2*inch, 4*inch])
        order_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(order_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Add order items
        items_data = [["Product", "Quantity", "Price", "Total"]]
        for item in order.orderitem_set.all():
            items_data.append([
                item.product.name,
                str(item.quantity),
                f"₹{item.price:.2f}",
                f"₹{(item.price * item.quantity):.2f}"
            ])
        
        # Add totals
        items_data.append(["Subtotal", "", "", f"₹{order.total_price:.2f}"])
        
        # Calculate GST (18% on 90% of amount as per Indian regulations)
        taxable_amount = order.total_price * Decimal('0.9')
        gst = taxable_amount * Decimal('0.18')
        
        items_data.append(["GST (18%)", "", "", f"₹{gst:.2f}"])
        
        # Apply membership discount if applicable
        discount = Decimal('0')
        if order.user.membership_status == 'P':
            discount = order.total_price * Decimal('0.1')  # 10% discount for premium members
            items_data.append(["Membership Discount (10%)", "", "", f"-₹{discount:.2f}"])
        
        # Calculate grand total
        grand_total = order.total_price + gst - discount
        items_data.append(["Grand Total", "", "", f"₹{grand_total:.2f}"])
        
        items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -4), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(items_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Add payment information
        payment_info = [
            ["Payment Information", ""],
            ["Payment Method:", payment.get_payment_method_display()],
            ["Transaction ID:", payment.transaction_id],
            ["Payment Date:", payment.created_at.strftime("%Y-%m-%d %H:%M")],
            ["Payment Status:", payment.get_status_display()]
        ]
        
        payment_table = Table(payment_info, colWidths=[2*inch, 4*inch])
        payment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('SPAN', (0, 0), (1, 0)),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 1), (0, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (0, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 12),
            ('BACKGROUND', (1, 1), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(payment_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Add terms and conditions
        terms_style = ParagraphStyle(
            'Terms',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey
        )
        terms = Paragraph(
            "Terms and Conditions: This is a computer-generated receipt and does not require a signature. " +
            "For any queries regarding this receipt, please contact our customer support.",
            terms_style
        )
        elements.append(terms)
        
        # Build the PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_booking_receipt(booking, payment):
        """
        Generate a PDF receipt for a booking.
        
        Args:
            booking: The Booking object
            payment: The Payment object
            
        Returns:
            BytesIO: A buffer containing the PDF data
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Add company logo if available
        logo_path = os.path.join(settings.STATIC_ROOT, 'images/logo.png')
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=2*inch, height=1*inch)
            elements.append(logo)
        
        # Add title
        title_style = styles['Heading1']
        title = Paragraph("Booking Receipt", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.25*inch))
        
        # Add booking information
        booking_info = [
            ["Booking Number:", f"#{booking.id}"],
            ["Date:", booking.created_at.strftime("%Y-%m-%d %H:%M")],
            ["Customer:", f"{booking.user.first_name} {booking.user.last_name}"],
            ["Email:", booking.user.email],
            ["Phone:", booking.user.phone_number],
            ["Status:", booking.get_status_display()]
        ]
        
        booking_table = Table(booking_info, colWidths=[2*inch, 4*inch])
        booking_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(booking_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Add service details
        service_data = [["Service", "Date", "Time", "Price"]]
        service_data.append([
            booking.service.name,
            booking.service_date.strftime("%Y-%m-%d"),
            booking.service_time.strftime("%H:%M"),
            f"₹{booking.service.price:.2f}"
        ])
        
        # Add totals
        service_data.append(["Subtotal", "", "", f"₹{booking.total_price:.2f}"])
        
        # Calculate GST (18% on 90% of amount as per Indian regulations)
        taxable_amount = booking.total_price * Decimal('0.9')
        gst = taxable_amount * Decimal('0.18')
        
        service_data.append(["GST (18%)", "", "", f"₹{gst:.2f}"])
        
        # Apply membership discount if applicable
        discount = Decimal('0')
        if booking.user.membership_status == 'P':
            discount = booking.total_price * Decimal('0.1')  # 10% discount for premium members
            service_data.append(["Membership Discount (10%)", "", "", f"-₹{discount:.2f}"])
        
        # Calculate grand total
        grand_total = booking.total_price + gst - discount
        service_data.append(["Grand Total", "", "", f"₹{grand_total:.2f}"])
        
        service_table = Table(service_data, colWidths=[3*inch, 1.5*inch, 1*inch, 1.5*inch])
        service_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -4), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(service_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Add payment information
        payment_info = [
            ["Payment Information", ""],
            ["Payment Method:", payment.get_payment_method_display()],
            ["Transaction ID:", payment.transaction_id],
            ["Payment Date:", payment.created_at.strftime("%Y-%m-%d %H:%M")],
            ["Payment Status:", payment.get_status_display()]
        ]
        
        payment_table = Table(payment_info, colWidths=[2*inch, 4*inch])
        payment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('SPAN', (0, 0), (1, 0)),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 1), (0, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (0, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 12),
            ('BACKGROUND', (1, 1), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(payment_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Add terms and conditions
        terms_style = ParagraphStyle(
            'Terms',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey
        )
        terms = Paragraph(
            "Terms and Conditions: This is a computer-generated receipt and does not require a signature. " +
            "For any queries regarding this receipt, please contact our customer support.",
            terms_style
        )
        elements.append(terms)
        
        # Build the PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer