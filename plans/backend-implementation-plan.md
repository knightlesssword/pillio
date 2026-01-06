# Pillio Health Hub - Backend Implementation Plan

## Overview
This document outlines the complete plan for implementing the FastAPI backend for the Pillio Medicine Management application. The backend will integrate with the existing React frontend and PostgreSQL database.

## Technology Stack
- **Backend Framework**: FastAPI with Python 3.11+
- **Database**: PostgreSQL with SQLAlchemy ORM (async)
- **Authentication**: JWT tokens (simple implementation)
- **File Storage**: Local filesystem (with future cloud integration capability)
- **Real-time**: Server-Sent Events (SSE)
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
│   │   ├── users.py           # User management
│   │   ├── medicines.py       # Medicine CRUD
│   │   ├── prescriptions.py   # Prescription CRUD
│   │   ├── reminders.py       # Reminder CRUD
│   │   ├── inventory.py       # Inventory management
│   │   ├── notifications.py   # Notification system
│   │   ├── dashboard.py       # Dashboard statistics
│   │   └── reports.py         # Analytics and reports
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── medicine_service.py
│   │   ├── reminder_service.py
│   │   ├── notification_service.py
│   │   └── file_service.py
│   ├── utils/                 # Utility functions
│   │   ├── __init__.py
│   │   ├── password.py        # Password hashing
│   │   ├── jwt.py            # JWT utilities
│   │   └── datetime.py       # Date/time helpers
│   └── core/                  # Core functionality
│       ├── __init__.py
│       ├── security.py        # Security configurations
│       └── exceptions.py      # Custom exceptions
├── tests/                     # Test files
├── uploads/                   # File storage directory
├── requirements.txt
├── .env.example
├── .gitignore
├── docker-compose.yml (optional)
└── README.md
```

## Implementation Phases

### Phase 1: Foundation Setup
1. **Project Structure Creation**
   - Create backend directory structure
   - Set up virtual environment and dependencies
   - Configure environment variables

2. **Database Configuration**
   - Set up SQLAlchemy async connection
   - Create base model classes
   - Implement database session management

3. **Core Models Implementation**
   - User model with authentication fields
   - Medicine model with inventory tracking
   - Prescription model with file associations
   - Reminder model with scheduling logic
   - ReminderLog model for tracking
   - Notification model for alerts

### Phase 2: Authentication System
1. **Security Setup**
   - JWT configuration and secret management
   - Password hashing with bcrypt
   - Token expiration handling

2. **Authentication Endpoints**
   - POST /auth/register - User registration
   - POST /auth/login - User login
   - POST /auth/refresh - Token refresh
   - POST /auth/logout - User logout

3. **User Management**
   - GET /users/me - Get current user profile
   - PUT /users/me - Update user profile
   - GET /users/stats - User statistics

### Phase 3: Core CRUD Operations
1. **Medicine Management**
   - GET /medicines - List medicines with filtering
   - POST /medicines - Create new medicine
   - GET /medicines/{id} - Get specific medicine
   - PUT /medicines/{id} - Update medicine
   - DELETE /medicines/{id} - Delete medicine

2. **Reminder System**
   - GET /reminders - List reminders with scheduling
   - POST /reminders - Create new reminder
   - PUT /reminders/{id} - Update reminder
   - DELETE /reminders/{id} - Delete reminder
   - POST /reminders/{id}/log - Log reminder completion

3. **Prescription Management**
   - GET /prescriptions - List prescriptions
   - POST /prescriptions - Create prescription (with file upload)
   - GET /prescriptions/{id} - Get prescription details
   - PUT /prescriptions/{id} - Update prescription
   - DELETE /prescriptions/{id} - Delete prescription

### Phase 4: Advanced Features
1. **Inventory Management**
   - POST /inventory/adjust - Adjust stock levels
   - GET /inventory/history - Stock change history
   - GET /inventory/alerts - Low stock notifications

2. **Notification System**
   - GET /notifications - User notifications
   - PUT /notifications/{id}/read - Mark as read
   - DELETE /notifications/{id} - Delete notification
   - SSE endpoint for real-time notifications

3. **Dashboard & Analytics**
   - GET /dashboard/stats - Dashboard statistics
   - GET /reports/adherence - Adherence reports
   - GET /reports/consumption - Consumption analytics

### Phase 5: File Handling & Storage
1. **File Upload System**
   - Image upload for prescriptions
   - File validation and security
   - Local storage management

2. **File Retrieval**
   - Secure file serving
   - Thumbnail generation
   - File deletion and cleanup

### Phase 6: Background Tasks & Scheduling
1. **Reminder Scheduling**
   - Background task for reminder notifications
   - Automatic stock level monitoring
   - Prescription expiry alerts

2. **Data Maintenance**
   - Database cleanup tasks
   - Log rotation and archiving
   - Cache management

## API Integration with Frontend

### Authentication Flow
1. Frontend sends login credentials to `/auth/login`
2. Backend validates and returns JWT token
3. Frontend stores token and includes in subsequent requests
4. Backend validates token for protected routes

### Data Flow
1. **Dashboard Data**: `/dashboard/stats` provides all dashboard metrics
2. **Medicine Management**: Full CRUD operations align with frontend forms
3. **Reminder System**: Real-time updates via SSE for active reminders
4. **Notifications**: Push notifications for low stock, missed reminders

### File Upload Process
1. Frontend sends multipart/form-data to prescription endpoints
2. Backend validates file type and size
3. File saved to local storage with UUID naming
4. File URL returned for frontend display

## Database Schema Alignment

The provided PostgreSQL schema will be implemented as SQLAlchemy models with the following considerations:

1. **Primary Keys**: All tables use integer IDs (SERIAL equivalent)
2. **Foreign Keys**: Proper cascading relationships maintained
3. **Indexes**: Database-level indexes for performance
4. **Data Types**: PostgreSQL types mapped to SQLAlchemy equivalents
5. **Timestamps**: Automatic timestamp handling with UTC

## Configuration & Environment

### Required Environment Variables
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost/pillio
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
UPLOAD_DIR=uploads
MAX_FILE_SIZE=5242880  # 5MB
ALLOWED_FILE_TYPES=jpg,jpeg,png,pdf
```

### Development Setup
1. Install Python dependencies
2. Configure PostgreSQL connection
3. Set up environment variables
4. Run database migrations
5. Start FastAPI development server

## Testing Strategy
1. **Unit Tests**: Test individual services and functions
2. **Integration Tests**: Test API endpoints with database
3. **Authentication Tests**: Test JWT and security flows
4. **File Upload Tests**: Test file handling functionality

## Next Steps
1. Create project structure and dependencies
2. Implement database models
3. Set up authentication system
4. Build core CRUD endpoints
5. Integrate with frontend
6. Add advanced features and optimization

This plan ensures a systematic approach to building a robust, scalable backend that perfectly integrates with the existing React frontend.