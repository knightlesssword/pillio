from datetime import datetime, date, time, timedelta
from typing import List, Optional
import pytz


def get_current_utc() -> datetime:
    """Get current UTC datetime"""
    return datetime.now(pytz.UTC)


def localize_datetime(dt: datetime, timezone_str: str = "UTC") -> datetime:
    """Localize a naive datetime to a specific timezone"""
    timezone = pytz.timezone(timezone_str)
    if dt.tzinfo is None:
        return timezone.localize(dt)
    return dt.astimezone(timezone)


def convert_to_utc(dt: datetime) -> datetime:
    """Convert a datetime to UTC"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=pytz.UTC)
    return dt.astimezone(pytz.UTC)


def get_date_range(days: int) -> tuple[date, date]:
    """Get a date range (start_date, end_date) for the last N days"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    return start_date, end_date


def get_month_range(year: int, month: int) -> tuple[date, date]:
    """Get the start and end date of a month"""
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    
    end_date = next_month - timedelta(days=1)
    start_date = date(year, month, 1)
    
    return start_date, end_date


def is_weekday(dt: datetime) -> bool:
    """Check if a datetime is a weekday (Monday-Friday)"""
    return dt.weekday() < 5  # 0=Monday, 6=Sunday


def get_weekday_names() -> List[str]:
    """Get list of weekday names"""
    return ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def parse_time_string(time_str: str) -> time:
    """Parse time string in HH:MM format"""
    return time.fromisoformat(time_str)


def format_time_for_display(time_obj: time) -> str:
    """Format time object for display (12-hour format)"""
    return time_obj.strftime("%I:%M %p")


def format_time_for_api(time_obj: time) -> str:
    """Format time object for API (24-hour format)"""
    return time_obj.strftime("%H:%M:%S")


def calculate_time_difference(dt1: datetime, dt2: datetime) -> timedelta:
    """Calculate time difference between two datetimes"""
    return dt1 - dt2


def is_time_in_range(check_time: time, start_time: time, end_time: time) -> bool:
    """Check if a time is within a range"""
    if start_time <= end_time:
        return start_time <= check_time <= end_time
    else:  # Handle overnight ranges
        return check_time >= start_time or check_time <= end_time


def get_next_occurrence(frequency: str, start_date: date, specific_days: Optional[List[int]] = None) -> date:
    """Get the next occurrence date based on frequency"""
    today = date.today()
    
    if today < start_date:
        return start_date
    
    if frequency == "daily":
        return today + timedelta(days=1)
    
    elif frequency == "weekly" and specific_days:
        current_weekday = today.weekday()  # 0=Monday, 6=Sunday
        
        # Find the next occurrence
        for day in sorted(specific_days):
            if day > current_weekday:
                days_ahead = day - current_weekday
                return today + timedelta(days=days_ahead)
        
        # If no day found this week, return next week's first day
        days_ahead = 7 - current_weekday + specific_days[0]
        return today + timedelta(days=days_ahead)
    
    elif frequency == "custom" and specific_days:
        # For custom frequency, assume weekly pattern
        return get_next_occurrence("weekly", start_date, specific_days)
    
    # Default to daily
    return today + timedelta(days=1)


def get_reminder_times_for_date(base_time: time, frequency: str, specific_days: Optional[List[int]] = None) -> List[time]:
    """Get all reminder times for a specific date"""
    if frequency == "daily":
        return [base_time]
    
    elif frequency == "weekly" and specific_days:
        # For weekly reminders, return time only if it's the right day
        # This function would need the date to check if it's the right day
        return [base_time]  # Simplified for now
    
    else:
        return [base_time]


def get_age_from_birthdate(birth_date: date) -> int:
    """Calculate age from birthdate"""
    today = date.today()
    age = today.year - birth_date.year
    
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    
    return age


def is_date_expired(check_date: date) -> bool:
    """Check if a date has expired"""
    return check_date < date.today()


def days_until_expiry(expiry_date: date) -> int:
    """Calculate days until expiry"""
    if expiry_date < date.today():
        return -1  # Already expired
    return (expiry_date - date.today()).days


def format_duration(days: int) -> str:
    """Format duration in days to human-readable string"""
    if days < 0:
        return "Expired"
    elif days == 0:
        return "Today"
    elif days == 1:
        return "1 day"
    elif days < 7:
        return f"{days} days"
    elif days < 30:
        weeks = days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''}"
    else:
        months = days // 30
        return f"{months} month{'s' if months > 1 else ''}"


def get_time_periods() -> dict[str, str]:
    """Get common time periods for reminders"""
    return {
        "morning": "06:00",
        "afternoon": "12:00", 
        "evening": "18:00",
        "night": "21:00"
    }


def combine_date_and_time(date_obj: date, time_obj: time) -> datetime:
    """Combine date and time objects into a datetime"""
    return datetime.combine(date_obj, time_obj)


def get_next_midnight(dt: datetime = None) -> datetime:
    """Get the next midnight after the given datetime"""
    if dt is None:
        dt = datetime.now()
    
    next_day = dt.date() + timedelta(days=1)
    return datetime.combine(next_day, time.min)