from fastapi import HTTPException, status


class AuthException(HTTPException):
    """Base authentication exception"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class PermissionException(HTTPException):
    """Permission denied exception"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class ValidationException(HTTPException):
    """Validation error exception"""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class NotFoundException(HTTPException):
    """Resource not found exception"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class ConflictException(HTTPException):
    """Resource conflict exception"""
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


class BadRequestException(HTTPException):
    """Bad request exception"""
    def __init__(self, detail: str = "Bad request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class MedicineNotFoundException(NotFoundException):
    """Medicine not found exception"""
    def __init__(self, medicine_id: int):
        super().__init__(detail=f"Medicine with ID {medicine_id} not found")


class ReminderNotFoundException(NotFoundException):
    """Reminder not found exception"""
    def __init__(self, reminder_id: int):
        super().__init__(detail=f"Reminder with ID {reminder_id} not found")


class PrescriptionNotFoundException(NotFoundException):
    """Prescription not found exception"""
    def __init__(self, prescription_id: int):
        super().__init__(detail=f"Prescription with ID {prescription_id} not found")


class UserNotFoundException(NotFoundException):
    """User not found exception"""
    def __init__(self, user_id: int):
        super().__init__(detail=f"User with ID {user_id} not found")


class NotificationNotFoundException(NotFoundException):
    """Notification not found exception"""
    def __init__(self, notification_id: int):
        super().__init__(detail=f"Notification with ID {notification_id} not found")


class InvalidCredentialsException(AuthException):
    """Invalid credentials exception"""
    def __init__(self):
        super().__init__(detail="Invalid email or password")


class InactiveUserException(AuthException):
    """Inactive user exception"""
    def __init__(self):
        super().__init__(detail="User account is inactive")


class UserAlreadyExistsException(ConflictException):
    """User already exists exception"""
    def __init__(self, email: str):
        super().__init__(detail=f"User with email {email} already exists")


class MedicineAlreadyExistsException(ConflictException):
    """Medicine already exists exception"""
    def __init__(self, name: str):
        super().__init__(detail=f"Medicine with name '{name}' already exists")


class InsufficientStockException(BadRequestException):
    """Insufficient stock exception"""
    def __init__(self, current_stock: int, requested: int):
        super().__init__(
            detail=f"Insufficient stock. Current: {current_stock}, Requested: {requested}"
        )


class InvalidReminderTimeException(ValidationException):
    """Invalid reminder time exception"""
    def __init__(self, time_str: str):
        super().__init__(detail=f"Invalid reminder time format: {time_str}")


class ReminderConflictException(ConflictException):
    """Reminder conflict exception"""
    def __init__(self, message: str = "Reminder time conflict detected"):
        super().__init__(detail=message)


class FileUploadException(HTTPException):
    """File upload exception"""
    def __init__(self, detail: str = "File upload failed"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class InvalidFileTypeException(FileUploadException):
    """Invalid file type exception"""
    def __init__(self, file_type: str, allowed_types: list):
        super().__init__(
            detail=f"Invalid file type: {file_type}. Allowed types: {', '.join(allowed_types)}"
        )


class FileTooLargeException(FileUploadException):
    """File too large exception"""
    def __init__(self, file_size: int, max_size: int):
        super().__init__(
            detail=f"File size {file_size} exceeds maximum allowed size {max_size}"
        )


class PrescribedMedicineNotFoundException(NotFoundException):
    """Prescribed medicine not found in user's medicines"""
    def __init__(self, medicine_name: str):
        super().__init__(detail=f"Prescribed medicine '{medicine_name}' not found in your medicine list")


class LowStockThresholdException(BadRequestException):
    """Low stock threshold exception"""
    def __init__(self, current_stock: int, threshold: int):
        super().__init__(
            detail=f"Current stock ({current_stock}) is below threshold ({threshold})"
        )


class ExpiredPrescriptionException(BadRequestException):
    """Expired prescription exception"""
    def __init__(self, prescription_id: int):
        super().__init__(detail=f"Prescription {prescription_id} has expired")


class InvalidReminderFrequencyException(ValidationException):
    """Invalid reminder frequency exception"""
    def __init__(self, frequency: str):
        super().__init__(detail=f"Invalid reminder frequency: {frequency}")


class DatabaseException(HTTPException):
    """Database operation exception"""
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


def raise_not_found(entity: str, entity_id: int):
    """Raise not found exception for an entity"""
    raise NotFoundException(f"{entity} with ID {entity_id} not found")


def raise_conflict(entity: str, detail: str = None):
    """Raise conflict exception for an entity"""
    if detail is None:
        detail = f"{entity} already exists"
    raise ConflictException(detail)


def raise_validation(detail: str):
    """Raise validation exception"""
    raise ValidationException(detail)


def raise_permission(detail: str = "Insufficient permissions"):
    """Raise permission exception"""
    raise PermissionException(detail)


def raise_auth(detail: str = "Authentication required"):
    """Raise authentication exception"""
    raise AuthException(detail)