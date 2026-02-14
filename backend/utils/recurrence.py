"""
Recurrence logic for recurring appointments
"""
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Tuple


def generate_recurring_dates(start_date: datetime.date, recurrence_type: str, 
                             recurrence_end: datetime.date) -> List[datetime.date]:
    """
    Generate list of dates for recurring appointments
    
    Args:
        start_date: initial appointment date
        recurrence_type: 'weekly' or 'monthly'
        recurrence_end: end date for recurrence
    
    Returns:
        List of dates for recurring appointments (excluding the initial date)
    """
    dates = []
    current_date = start_date
    
    if recurrence_type == 'weekly':
        # Generate weekly occurrences
        while True:
            current_date = current_date + timedelta(weeks=1)
            if current_date > recurrence_end:
                break
            dates.append(current_date)
    
    elif recurrence_type == 'monthly':
        # Generate monthly occurrences
        while True:
            current_date = current_date + relativedelta(months=1)
            if current_date > recurrence_end:
                break
            dates.append(current_date)
    
    return dates


def get_next_occurrence(start_date: datetime.date, recurrence_type: str) -> datetime.date:
    """
    Get the next occurrence date based on recurrence type
    
    Args:
        start_date: current occurrence date
        recurrence_type: 'weekly' or 'monthly'
    
    Returns:
        Next occurrence date
    """
    if recurrence_type == 'weekly':
        return start_date + timedelta(weeks=1)
    elif recurrence_type == 'monthly':
        return start_date + relativedelta(months=1)
    
    return start_date


def calculate_occurrences_count(start_date: datetime.date, recurrence_type: str,
                                recurrence_end: datetime.date) -> int:
    """
    Calculate the number of occurrences for a recurring appointment
    
    Args:
        start_date: initial appointment date
        recurrence_type: 'weekly' or 'monthly'
        recurrence_end: end date for recurrence
    
    Returns:
        Number of occurrences (including the initial appointment)
    """
    if recurrence_type == 'none':
        return 1
    
    dates = generate_recurring_dates(start_date, recurrence_type, recurrence_end)
    return len(dates) + 1  # +1 for the initial appointment
