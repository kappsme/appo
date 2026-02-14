"""
Email notification service for appointment booking
"""
from flask_mail import Mail, Message
from flask import current_app
import logging

mail = Mail()
logger = logging.getLogger(__name__)


def init_mail(app):
    """Initialize mail service with Flask app"""
    mail.init_app(app)


def send_appointment_confirmation(appointment_data):
    """
    Send confirmation email for a new appointment
    
    Args:
        appointment_data: dict with appointment details
    """
    try:
        client_name = appointment_data.get('client', 'Cliente')
        date = appointment_data.get('date', '')
        time = appointment_data.get('time', '')
        service = appointment_data.get('service_name', 'Servicio')
        
        subject = f'Confirmación de Cita - {date}'
        
        body = f"""
        Hola {client_name},
        
        Tu cita ha sido confirmada exitosamente:
        
        📅 Fecha: {date}
        🕐 Hora: {time}
        💼 Servicio: {service}
        
        Si necesitas cancelar o modificar tu cita, por favor contáctanos con anticipación.
        
        ¡Gracias por tu preferencia!
        
        ---
        Sistema de Agendamiento APPO
        """
        
        # For now, just log the email since we might not have SMTP configured
        logger.info(f"Email would be sent to client: {client_name}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Body: {body}")
        
        # Uncomment when SMTP is configured
        # msg = Message(
        #     subject,
        #     recipients=[appointment_data.get('email')],
        #     body=body
        # )
        # mail.send(msg)
        
        return True
    except Exception as e:
        logger.error(f"Error sending confirmation email: {str(e)}")
        return False


def send_appointment_reminder(appointment_data):
    """
    Send reminder email 24 hours before appointment
    
    Args:
        appointment_data: dict with appointment details
    """
    try:
        client_name = appointment_data.get('client', 'Cliente')
        date = appointment_data.get('date', '')
        time = appointment_data.get('time', '')
        service = appointment_data.get('service_name', 'Servicio')
        
        subject = f'Recordatorio de Cita - Mañana {date}'
        
        body = f"""
        Hola {client_name},
        
        Este es un recordatorio de tu cita programada para mañana:
        
        📅 Fecha: {date}
        🕐 Hora: {time}
        💼 Servicio: {service}
        
        Por favor, llega 5-10 minutos antes de tu cita.
        
        Si necesitas cancelar, por favor avísanos lo antes posible.
        
        ¡Te esperamos!
        
        ---
        Sistema de Agendamiento APPO
        """
        
        logger.info(f"Reminder email would be sent to: {client_name}")
        logger.info(f"Subject: {subject}")
        
        return True
    except Exception as e:
        logger.error(f"Error sending reminder email: {str(e)}")
        return False


def send_cancellation_confirmation(appointment_data):
    """
    Send confirmation email for cancelled appointment
    
    Args:
        appointment_data: dict with appointment details
    """
    try:
        client_name = appointment_data.get('client', 'Cliente')
        date = appointment_data.get('date', '')
        time = appointment_data.get('time', '')
        
        subject = f'Cancelación de Cita - {date}'
        
        body = f"""
        Hola {client_name},
        
        Tu cita ha sido cancelada:
        
        📅 Fecha: {date}
        🕐 Hora: {time}
        
        Si deseas reagendar, puedes hacerlo en cualquier momento a través de nuestro sistema.
        
        Gracias por avisarnos.
        
        ---
        Sistema de Agendamiento APPO
        """
        
        logger.info(f"Cancellation email would be sent to: {client_name}")
        logger.info(f"Subject: {subject}")
        
        return True
    except Exception as e:
        logger.error(f"Error sending cancellation email: {str(e)}")
        return False
