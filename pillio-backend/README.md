# Pillio Health Hub - Backend API

A FastAPI backend for managing medications, reminders, prescriptions, and inventory for personal health management.

## ⚠️ MEDICAL DISCLAIMER

**IMPORTANT: READ BEFORE USING**

This application is designed for **personal medication tracking and inventory management only**. It is **NOT intended to provide medical advice, diagnosis, or treatment**.

### Key Points:
- **NOT Medical Advice**: This application does not provide medical advice, diagnosis, or treatment recommendations
- **Personal Use Only**: This tool is for organizing your personal medication information
- **Consult Healthcare Professionals**: Always consult with your doctor, pharmacist, or other qualified healthcare provider regarding any medication decisions
- **User Responsibility**: All medication management decisions are solely at your discretion and responsibility
- **No Liability**: The developers and maintainers of this application are not liable for any misuse, malpractices, or issues arising from the use of this application or any of its parts.
- **Emergency Situations**: In case of medical emergencies, contact your healthcare provider or emergency services immediately

### Intended Use:
- Tracking medication schedules and reminders
- Organizing prescription information
- Monitoring personal medication inventory
- Maintaining medication history records

### NOT Intended For:
- Self-diagnosis or self-treatment
- Replacing professional medical advice
- Making critical healthcare decisions
- Emergency medical situations

**By using this application, you acknowledge that you understand and accept this disclaimer.**

## Features

- **User Authentication**: JWT-based authentication with Argon2 password hashing
- **Medicine Management**: CRUD operations for personal medicine inventory
- **Reminder System**: Create and manage medication reminders with flexible scheduling
- **Prescription Tracking**: Upload and manage prescription documents
- **Inventory Management**: Track stock levels and history
- **Notification System**: Real-time notifications for reminders and low stock
- **Dashboard Analytics**: Statistics and adherence tracking
- **Admin Panel**: User management and system administration

## Tech Stack

- **Framework**: FastAPI with Python 3.11+
- **Database**: PostgreSQL with SQLAlchemy ORM (async)
- **Authentication**: JWT tokens with Argon2 password hashing
- **File Storage**: Local filesystem (with cloud integration capability)
- **Real-time**: Server-Sent Events (SSE) for notifications
- **API Documentation**: Automatic with FastAPI

## Project Structure

```
pillio-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database connection and session
│   ├── models/                # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── medicine.py
│   │   ├── prescription.py
│   │   ├── reminder.py
│   │   ├── reminder_log.py
│   │   ├── inventory_history.py
│   │   └── notification.py
│   ├── schemas/               # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── medicine.py
│   │   ├── prescription.py
│   │   ├── reminder.py
│   │   └── common.py
│   ├── api/                   # API routes
│   │   ├── __init__.py
│   │   ├── deps.py            # Dependencies
│   │   ├── auth.py            # Authentication routes
│   │   └── users.py           # User management
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   └── auth_service.py
│   ├── utils/                 # Utility functions
│   │   ├── __init__.py
│   │   ├── password.py        # Password hashing
│   │   ├── jwt.py            # JWT utilities
│   │   └── datetime.py       # Date/time helpers
│   └── core/                  # Core functionality
│       ├── __init__.py
│       ├── security.py        # Security configurations
│       └── exceptions.py      # Custom exceptions
├── uploads/                   # File storage directory
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database
- pip or conda for package management

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd pillio-health-hub-main/pillio-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\\Scripts\\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

Make sure PostgreSQL is running and create a database:

```sql
CREATE DATABASE pillio;
CREATE USER pillio_user WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE pillio TO pillio_user;
```

### 4. Environment Configuration

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://pillio_user:your_password@localhost:5432/pillio

# Security Configuration
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload Configuration
UPLOAD_DIR=uploads
MAX_FILE_SIZE=5242880  # 5MB
ALLOWED_FILE_TYPES=jpg,jpeg,png,pdf

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

### 5. Run the Application

#### Development Mode

```bash
# Start the development server with auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or run directly
python app/main.py
```

#### Production Mode

```bash
# Start with production settings
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user profile
- `PUT /api/v1/auth/me` - Update user profile
- `POST /api/v1/auth/change-password` - Change password

### User Management

- `GET /api/v1/users/profile` - Get user profile
- `PUT /api/v1/users/profile` - Update user profile
- `DELETE /api/v1/users/account` - Delete user account
- `GET /api/v1/users/stats` - Get user statistics

### Admin Endpoints

- `GET /api/v1/users/` - Get all users (admin only)
- `GET /api/v1/users/{user_id}` - Get user by ID (admin only)
- `PUT /api/v1/users/{user_id}/activate` - Activate user (admin only)
- `PUT /api/v1/users/{user_id}/deactivate` - Deactivate user (admin only)

## Database Schema

The application uses the following main tables:

- **users**: User accounts and profiles
- **medicines**: Medicine inventory and details
- **prescriptions**: Prescription documents and details
- **reminders**: Medication reminders and scheduling
- **reminder_logs**: History of reminder completions
- **inventory_history**: Stock change history
- **notifications**: User notifications and alerts

## Security Features

- **Password Hashing**: Argon2 hashing for secure password storage
- **JWT Authentication**: Access and refresh token system
- **CORS Configuration**: Configurable cross-origin resource sharing
- **Input Validation**: Pydantic schemas for request validation
- **Error Handling**: Custom exception handling with appropriate HTTP status codes
- **Rate Limiting**: Built-in FastAPI rate limiting capabilities

## File Upload

The application supports file uploads for prescription images:

- **Max File Size**: 5MB (configurable)
- **Allowed Types**: JPG, JPEG, PNG, PDF
- **Storage**: Local filesystem (uploads directory)
- **Future**: Cloud storage integration capability

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | 30 |
| `UPLOAD_DIR` | File upload directory | uploads |
| `MAX_FILE_SIZE` | Maximum file upload size | 5242880 (5MB) |
| `ALLOWED_ORIGINS` | CORS allowed origins | ["http://localhost:8080"] |
| `DEBUG` | Enable debug mode | True |

## Testing

```bash
# Run tests (when implemented)
pytest

# Run with coverage
pytest --cov=app tests/
```

## Deployment

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Gunicorn

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Development Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Use async/await for database operations

### Database Migrations

For database schema changes, consider using Alembic:

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### API Design

- RESTful endpoint design
- Consistent response formats
- Proper HTTP status codes
- Comprehensive error messages
- Input validation and sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository or contact the development team.