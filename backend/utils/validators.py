"""
Validation utilities for the appointment booking system
"""
import re
from datetime import datetime, time, timedelta
from typing import Tuple, Optional


def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Remove common separators
    phone = re.sub(r'[\s\-\(\)]+', '', phone)
    # Check if it's a valid phone number (between 7 and 15 digits)
    return bool(re.match(r'^\+?[0-9]{7,15}$', phone))


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_time_range(start_time: time, end_time: time) -> bool:
    """Validate that end_time is after start_time"""
    return end_time > start_time


def validate_appointment_slot(date, time_slot, duration_minutes, existing_appointments) -> Tuple[bool, Optional[str]]:
    """
    Validate if an appointment slot is available
    
    Args:
        date: appointment date
        time_slot: appointment time
        duration_minutes: duration of the appointment
        existing_appointments: list of existing appointments for that date
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    appointment_datetime = datetime.combine(date, time_slot)
    appointment_end = appointment_datetime + timedelta(minutes=duration_minutes)
    
    for existing in existing_appointments:
        existing_start = datetime.combine(existing.date, existing.time)
        # Get duration from service or use default
        existing_duration = existing.service.duration if existing.service else 60
        existing_end = existing_start + timedelta(minutes=existing_duration)
        
        # Check for overlap
        if (appointment_datetime < existing_end and appointment_end > existing_start):
            return False, f"This time slot conflicts with an existing appointment at {existing.time.strftime('%H:%M')}"
    
    return True, None


def validate_date_range(start_date, end_date) -> bool:
    """Validate that end_date is after or equal to start_date"""
    return end_date >= start_date


def validate_recurrence(recurrence_type: str, recurrence_end=None, start_date=None) -> Tuple[bool, Optional[str]]:
    """
    Validate recurrence settings
    
    Args:
        recurrence_type: type of recurrence (none, weekly, monthly)
        recurrence_end: end date for recurrence
        start_date: start date of the appointment
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_types = ['none', 'weekly', 'monthly']
    
    if recurrence_type not in valid_types:
        return False, f"Invalid recurrence type. Must be one of: {', '.join(valid_types)}"
    
    if recurrence_type != 'none':
        if not recurrence_end:
            return False, "Recurrence end date is required for recurring appointments"
        
        if start_date and recurrence_end < start_date:
            return False, "Recurrence end date must be after the start date"
    
    return True, None


def sanitize_string(text: str, max_length: int = 255) -> str:
    """Sanitize and truncate string input"""
    if not text:
        return ""
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
    
    return text


def validate_duration(duration_minutes: int) -> bool:
    """Validate appointment duration"""
    # Duration should be between 15 minutes and 8 hours
    return 15 <= duration_minutes <= 480
