"""
Main Flask application for appointment booking system
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime, date, time, timedelta
import logging

from config import Config
from models import db, Appointment, Availability, Service, RecurrenceRule
from utils.validators import (
    validate_phone, validate_appointment_slot, 
    validate_recurrence, sanitize_string, validate_duration
)
from utils.email_service import (
    init_mail, send_appointment_confirmation,
    send_cancellation_confirmation
)
from utils.recurrence import generate_recurring_dates, calculate_occurrences_count

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
CORS(app)
init_mail(app)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_date(date_string):
    """Parse date string to date object"""
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


def parse_time(time_string):
    """Parse time string to time object"""
    try:
        return datetime.strptime(time_string, '%H:%M').time()
    except (ValueError, TypeError):
        return None


# ============================================================================
# ROUTES - CLIENT PANEL
# ============================================================================

@app.route('/')
def index():
    """Client booking page"""
    return render_template('index.html')


@app.route('/admin')
def admin():
    """Admin panel page"""
    return render_template('admin.html')


# ============================================================================
# API ENDPOINTS - SERVICES
# ============================================================================

@app.route('/api/services', methods=['GET'])
def get_services():
    """Get all active services"""
    try:
        services = Service.query.filter_by(active=True).all()
        return jsonify({
            'success': True,
            'services': [s.to_dict() for s in services]
        })
    except Exception as e:
        logger.error(f"Error getting services: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/services', methods=['POST'])
def create_service():
    """Create a new service"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'success': False, 'error': 'Service name is required'}), 400
        
        # Create service
        service = Service(
            name=sanitize_string(data['name'], 100),
            description=sanitize_string(data.get('description', ''), 500),
            duration=data.get('duration', 60),
            price=data.get('price', 0.0),
            active=data.get('active', True)
        )
        
        # Validate duration
        if not validate_duration(service.duration):
            return jsonify({'success': False, 'error': 'Invalid duration'}), 400
        
        db.session.add(service)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'service': service.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating service: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/services/<int:service_id>', methods=['PUT'])
def update_service(service_id):
    """Update a service"""
    try:
        service = Service.query.get_or_404(service_id)
        data = request.json
        
        # Update fields
        if 'name' in data:
            service.name = sanitize_string(data['name'], 100)
        if 'description' in data:
            service.description = sanitize_string(data['description'], 500)
        if 'duration' in data:
            if not validate_duration(data['duration']):
                return jsonify({'success': False, 'error': 'Invalid duration'}), 400
            service.duration = data['duration']
        if 'price' in data:
            service.price = data['price']
        if 'active' in data:
            service.active = data['active']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'service': service.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating service: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/services/<int:service_id>', methods=['DELETE'])
def delete_service(service_id):
    """Delete (deactivate) a service"""
    try:
        service = Service.query.get_or_404(service_id)
        service.active = False
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting service: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# API ENDPOINTS - AVAILABILITY
# ============================================================================

@app.route('/api/availability', methods=['GET'])
def get_availability():
    """Get availability configuration for all days"""
    try:
        availability = Availability.query.all()
        return jsonify({
            'success': True,
            'availability': [a.to_dict() for a in availability]
        })
    except Exception as e:
        logger.error(f"Error getting availability: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/availability', methods=['POST'])
def create_availability():
    """Create availability for a day of the week"""
    try:
        data = request.json
        
        # Parse times
        start_time = parse_time(data.get('start_time'))
        end_time = parse_time(data.get('end_time'))
        
        if not start_time or not end_time:
            return jsonify({'success': False, 'error': 'Invalid time format'}), 400
        
        if start_time >= end_time:
            return jsonify({'success': False, 'error': 'End time must be after start time'}), 400
        
        # Create availability
        availability = Availability(
            day_of_week=data.get('day_of_week'),
            start_time=start_time,
            end_time=end_time,
            duration_minutes=data.get('duration_minutes', 60),
            enabled=data.get('enabled', True)
        )
        
        db.session.add(availability)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'availability': availability.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating availability: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/availability/<int:availability_id>', methods=['PUT'])
def update_availability(availability_id):
    """Update availability configuration"""
    try:
        availability = Availability.query.get_or_404(availability_id)
        data = request.json
        
        # Update fields
        if 'start_time' in data:
            start_time = parse_time(data['start_time'])
            if start_time:
                availability.start_time = start_time
        
        if 'end_time' in data:
            end_time = parse_time(data['end_time'])
            if end_time:
                availability.end_time = end_time
        
        if availability.start_time >= availability.end_time:
            return jsonify({'success': False, 'error': 'End time must be after start time'}), 400
        
        if 'duration_minutes' in data:
            availability.duration_minutes = data['duration_minutes']
        if 'enabled' in data:
            availability.enabled = data['enabled']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'availability': availability.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating availability: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/availability/<int:availability_id>', methods=['DELETE'])
def delete_availability(availability_id):
    """Delete availability configuration"""
    try:
        availability = Availability.query.get_or_404(availability_id)
        db.session.delete(availability)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting availability: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# API ENDPOINTS - AVAILABLE SLOTS
# ============================================================================

@app.route('/api/available-slots/<date_string>', methods=['GET'])
def get_available_slots(date_string):
    """Get available time slots for a specific date"""
    try:
        # Parse date
        target_date = parse_date(date_string)
        if not target_date:
            return jsonify({'success': False, 'error': 'Invalid date format'}), 400
        
        # Get day of week (0 = Monday, 6 = Sunday)
        day_of_week = target_date.weekday()
        
        # Get availability for this day
        availability = Availability.query.filter_by(
            day_of_week=day_of_week,
            enabled=True
        ).first()
        
        if not availability:
            return jsonify({
                'success': True,
                'slots': []
            })
        
        # Get existing appointments for this date
        existing_appointments = Appointment.query.filter(
            Appointment.date == target_date,
            Appointment.status == 'active'
        ).all()
        
        # Generate time slots
        slots = []
        current_time = availability.start_time
        slot_duration = timedelta(minutes=availability.duration_minutes)
        
        while current_time < availability.end_time:
            # Check if this slot is available
            is_available = True
            
            for appointment in existing_appointments:
                if appointment.time == current_time:
                    is_available = False
                    break
            
            slots.append({
                'time': current_time.strftime('%H:%M'),
                'available': is_available
            })
            
            # Move to next slot
            dt = datetime.combine(date.today(), current_time) + slot_duration
            current_time = dt.time()
        
        return jsonify({
            'success': True,
            'slots': slots
        })
    except Exception as e:
        logger.error(f"Error getting available slots: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# API ENDPOINTS - APPOINTMENTS
# ============================================================================

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    """Get appointments with optional filtering"""
    try:
        # Get query parameters
        date_str = request.args.get('date')
        status = request.args.get('status', 'active')
        
        # Build query
        query = Appointment.query
        
        if date_str:
            target_date = parse_date(date_str)
            if target_date:
                query = query.filter_by(date=target_date)
        
        if status:
            query = query.filter_by(status=status)
        
        # Order by date and time
        appointments = query.order_by(Appointment.date, Appointment.time).all()
        
        return jsonify({
            'success': True,
            'appointments': [a.to_dict() for a in appointments]
        })
    except Exception as e:
        logger.error(f"Error getting appointments: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    """Create a new appointment"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['date', 'time', 'client', 'phone', 'service_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        # Parse date and time
        appointment_date = parse_date(data['date'])
        appointment_time = parse_time(data['time'])
        
        if not appointment_date or not appointment_time:
            return jsonify({'success': False, 'error': 'Invalid date or time format'}), 400
        
        # Validate phone
        if not validate_phone(data['phone']):
            return jsonify({'success': False, 'error': 'Invalid phone number'}), 400
        
        # Get service
        service = Service.query.get(data['service_id'])
        if not service:
            return jsonify({'success': False, 'error': 'Service not found'}), 404
        
        # Validate recurrence
        recurrence_type = data.get('recurrence', 'none')
        recurrence_end_date = None
        
        if recurrence_type != 'none':
            recurrence_end_str = data.get('recurrence_end')
            if recurrence_end_str:
                recurrence_end_date = parse_date(recurrence_end_str)
            
            is_valid, error_msg = validate_recurrence(
                recurrence_type, recurrence_end_date, appointment_date
            )
            if not is_valid:
                return jsonify({'success': False, 'error': error_msg}), 400
        
        # Check for conflicts
        existing_appointments = Appointment.query.filter(
            Appointment.date == appointment_date,
            Appointment.status == 'active'
        ).all()
        
        is_valid, error_msg = validate_appointment_slot(
            appointment_date, appointment_time, service.duration, existing_appointments
        )
        
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Create main appointment
        appointment = Appointment(
            date=appointment_date,
            time=appointment_time,
            client=sanitize_string(data['client'], 100),
            phone=sanitize_string(data['phone'], 20),
            service_id=data['service_id'],
            recurrence=recurrence_type,
            recurrence_end=recurrence_end_date,
            notes=sanitize_string(data.get('notes', ''), 500),
            status='active'
        )
        
        db.session.add(appointment)
        db.session.flush()  # Get the ID before creating recurring appointments
        
        # Create recurring appointments if needed
        if recurrence_type != 'none' and recurrence_end_date:
            recurring_dates = generate_recurring_dates(
                appointment_date, recurrence_type, recurrence_end_date
            )
            
            for recurring_date in recurring_dates:
                # Check for conflicts on each date
                existing = Appointment.query.filter(
                    Appointment.date == recurring_date,
                    Appointment.time == appointment_time,
                    Appointment.status == 'active'
                ).first()
                
                if not existing:
                    recurring_appointment = Appointment(
                        date=recurring_date,
                        time=appointment_time,
                        client=appointment.client,
                        phone=appointment.phone,
                        service_id=appointment.service_id,
                        recurrence='none',  # Child appointments don't recur
                        parent_appointment_id=appointment.id,
                        notes=appointment.notes,
                        status='active'
                    )
                    db.session.add(recurring_appointment)
        
        db.session.commit()
        
        # Send confirmation email
        send_appointment_confirmation({
            'client': appointment.client,
            'date': appointment.date.strftime('%Y-%m-%d'),
            'time': appointment.time.strftime('%H:%M'),
            'service_name': service.name
        })
        
        return jsonify({
            'success': True,
            'appointment': appointment.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating appointment: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/appointments/<int:appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    """Update an appointment"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        data = request.json
        
        # Update allowed fields
        if 'client' in data:
            appointment.client = sanitize_string(data['client'], 100)
        if 'phone' in data:
            if not validate_phone(data['phone']):
                return jsonify({'success': False, 'error': 'Invalid phone number'}), 400
            appointment.phone = sanitize_string(data['phone'], 20)
        if 'notes' in data:
            appointment.notes = sanitize_string(data['notes'], 500)
        if 'status' in data:
            appointment.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'appointment': appointment.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating appointment: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/appointments/<int:appointment_id>', methods=['DELETE'])
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        appointment.status = 'cancelled'
        
        # If this is a parent appointment, optionally cancel all children
        cancel_all = request.args.get('cancel_all', 'false').lower() == 'true'
        if cancel_all and appointment.children:
            for child in appointment.children:
                child.status = 'cancelled'
        
        db.session.commit()
        
        # Send cancellation email
        send_cancellation_confirmation({
            'client': appointment.client,
            'date': appointment.date.strftime('%Y-%m-%d'),
            'time': appointment.time.strftime('%H:%M')
        })
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error cancelling appointment: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Resource not found'}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    logger.error(f"Internal error: {str(error)}")
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
    return "Internal Server Error", 500


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

@app.cli.command('init-db')
def init_db():
    """Initialize the database"""
    with app.app_context():
        db.create_all()
        logger.info("Database tables created successfully")
        
        # Create default services if none exist
        if Service.query.count() == 0:
            default_services = [
                Service(name='Consulta General', description='Consulta médica general', duration=30, price=50.0),
                Service(name='Consulta Especializada', description='Consulta con especialista', duration=45, price=80.0),
                Service(name='Revisión', description='Revisión médica completa', duration=60, price=100.0)
            ]
            for service in default_services:
                db.session.add(service)
            
            db.session.commit()
            logger.info("Default services created")
        
        # Create default availability if none exists
        if Availability.query.count() == 0:
            # Monday to Friday, 9 AM to 6 PM
            for day in range(5):
                availability = Availability(
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(18, 0),
                    duration_minutes=60,
                    enabled=True
                )
                db.session.add(availability)
            
            db.session.commit()
            logger.info("Default availability created")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)