# 💊 Pillio 

A comprehensive personal medication management and health tracking application. Pillio helps you organize your medications, set reminders, track prescriptions, and monitor your medication inventory all in one place.

![Pillio Health Hub](https://img.shields.io/badge/Pillio-Health%20Hub-blue)
![React](https://img.shields.io/badge/React-18.3.1-61dafb)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688)
![TypeScript](https://img.shields.io/badge/TypeScript-5.8.3-3178c6)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-4169e1)

## ⚠️ Medical Disclaimer

**IMPORTANT: READ BEFORE USING**

This application is designed for **personal medication tracking and inventory management only**. It is **NOT intended to provide medical advice, diagnosis, or treatment**.

### Key Points:
- **NOT Medical Advice**: This application does not provide medical advice, diagnosis, or treatment recommendations
- **Personal Use Only**: This tool is for organizing your personal medication information
- **Consult Healthcare Professionals**: Always consult with your doctor, pharmacist, or other qualified healthcare provider regarding any medication decisions
- **User Responsibility**: All medication management decisions are solely at your discretion and responsibility
- **No Liability**: The developers and maintainers of this application are not liable for any misuse, malpractices, or issues arising from the use of this application
- **Emergency Situations**: In case of medical emergencies, contact your healthcare provider or emergency services immediately

**By using this application, you acknowledge that you understand and accept this disclaimer.**


## Screenshot
<img width="1893" height="966" alt="image" src="https://github.com/user-attachments/assets/4a26a680-8329-479c-af25-d9eb7dff0055" />


## Features

### Core Features
- **📊 Dashboard** - Overview of your medication status, upcoming reminders, and adherence statistics
- **💊 Medicine Management** - Add, edit, and manage your personal medicine inventory
- **⏰ Medication Reminders** - Create and manage medication schedules with flexible timing options
- **📝 Prescription Tracking** - Upload and organize prescription documents with associated medications
- **📦 Inventory Management** - Track stock levels and receive low stock alerts
- **🔔 Real-time Notifications** - Get notified about reminders and important updates
- **📈 Analytics & Reports** - View adherence statistics and generate reports
- **🔍 Universal Search** - Search across medicines, prescriptions, and reminders

### Additional Features
- **📱 Responsive Design** - Works on desktop and mobile devices
- **🌙 Dark Mode Support** - Easy on the eyes with dark theme
- **📤 Data Export** - Export your data in various formats
- **🔐 Secure Authentication** - JWT-based authentication with secure password hashing
- **📅 Calendar View** - Visualize your medication schedule
- **📊 History Tracking** - Complete history of medication adherence and inventory changes

## Tech Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS with shadcn/ui components
- **State Management**: React Query (TanStack Query) + Context API
- **Routing**: React Router DOM 6
- **Forms**: React Hook Form with Zod validation
- **Charts**: Recharts for analytics visualization
- **Icons**: Lucide React
- **Notifications**: Sonner + Radix UI Toast

### Backend
- **Framework**: FastAPI with Python 3.11+
- **Database**: PostgreSQL with SQLAlchemy Async ORM
- **Authentication**: JWT tokens with Argon2 password hashing
- **Task Scheduling**: APScheduler for reminder notifications
- **API Documentation**: Auto-generated with Swagger/OpenAPI
- **File Handling**: Local filesystem storage with Pillow for images


## Project Structure

```
pillio-health-hub/
├── src/                          # Frontend application
│   ├── components/               # Reusable UI components
│   │   ├── analytics/           # Charts and analytics components
│   │   ├── common/              # Shared components
│   │   ├── dashboard/           # Dashboard widgets
│   │   ├── inventory/           # Inventory management
│   │   ├── layout/              # Layout components (Navbar, Sidebar)
│   │   ├── medicine/            # Medicine-related components
│   │   ├── notifications/       # Notification components
│   │   ├── prescription/        # Prescription components
│   │   ├── reminder/            # Reminder components
│   │   ├── search/              # Search components
│   │   ├── settings/            # Settings components
│   │   └── ui/                  # shadcn/ui components
│   ├── contexts/                # React contexts (Auth, Notifications)
│   ├── lib/                     # Utility functions and API clients
│   ├── pages/                   # Page components
│   │   ├── auth/                # Authentication pages
│   │   ├── DashboardPage.tsx
│   │   ├── HistoryPage.tsx
│   │   ├── InventoryPage.tsx
│   │   ├── MedicinesPage.tsx
│   │   ├── PrescriptionsPage.tsx
│   │   ├── RemindersPage.tsx
│   │   ├── ReportsPage.tsx
│   │   └── SettingsPage.tsx
│   ├── App.tsx                  # Main application component
│   ├── main.tsx                 # Application entry point
│   └── index.css                # Global styles
├── pillio-backend/              # Backend application
│   ├── app/
│   │   ├── api/                 # API routes
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   ├── medicines.py     # Medicine endpoints
│   │   │   ├── notifications.py # Notification endpoints
│   │   │   ├── prescriptions.py # Prescription endpoints
│   │   │   ├── reminders.py     # Reminder endpoints
│   │   │   ├── search.py        # Search endpoints
│   │   │   ├── users.py         # User endpoints
│   │   │   └── deps.py          # API dependencies
│   │   ├── core/                # Core functionality
│   │   │   ├── exceptions.py    # Custom exceptions
│   │   │   ├── scheduler.py     # Task scheduler
│   │   │   └── security.py      # Security configurations
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── base.py
│   │   │   ├── inventory_history.py
│   │   │   ├── medicine.py
│   │   │   ├── notification.py
│   │   │   ├── prescription.py
│   │   │   ├── prescription_medicine.py
│   │   │   ├── reminder.py
│   │   │   ├── reminder_log.py
│   │   │   └── user.py
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── common.py
│   │   │   ├── inventory_history.py
│   │   │   ├── medicine.py
│   │   │   ├── notification.py
│   │   │   ├── prescription.py
│   │   │   ├── reminder.py
│   │   │   └── user.py
│   │   ├── services/            # Business logic
│   │   │   ├── auth_service.py
│   │   │   ├── export_service.py
│   │   │   ├── medicine_service.py
│   │   │   ├── notification_service.py
│   │   │   ├── notification_triggers.py
│   │   │   ├── prescription_service.py
│   │   │   └── reminder_service.py
│   │   ├── utils/               # Utility functions
│   │   │   ├── datetime.py
│   │   │   ├── jwt.py
│   │   │   └── password.py
│   │   ├── config.py            # Configuration
│   │   ├── database.py          # Database connection
│   │   └── main.py              # FastAPI application entry
│   ├── uploads/                 # File uploads directory
│   ├── requirements.txt         # Python dependencies
│   └── README.md                # Backend-specific README
├── public/                      # Static assets
├── package.json                 # Frontend dependencies
├── vite.config.ts               # Vite configuration
└── README.md                    # This file
```

## Getting Started

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **PostgreSQL** 14+

### Frontend Setup

```bash
# Navigate to project root
cd pillio

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:8080`

### Backend Setup

```bash
# Navigate to backend directory
cd pillio-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your database and security settings

# Start the development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend API will be available at `http://localhost:8000`

### Environment Variables

#### Backend (.env)

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/pillio

# Security Configuration
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# File Upload Configuration
UPLOAD_DIR=uploads
MAX_FILE_SIZE=5242880  # 5MB
ALLOWED_FILE_TYPES=jpg,jpeg,png,pdf

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Scheduler Configuration
SCHEDULER_API_ENABLED=true
```

## API Documentation

Once the backend is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Main API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user profile
- `PUT /api/v1/auth/me` - Update user profile

#### Medicines
- `GET /api/v1/medicines` - List all medicines
- `POST /api/v1/medicines` - Create new medicine
- `GET /api/v1/medicines/{id}` - Get medicine details
- `PUT /api/v1/medicines/{id}` - Update medicine
- `DELETE /api/v1/medicines/{id}` - Delete medicine
- `POST /api/v1/medicines/{id}/adjust-stock` - Adjust stock level

#### Reminders
- `GET /api/v1/reminders` - List all reminders
- `POST /api/v1/reminders` - Create new reminder
- `GET /api/v1/reminders/{id}` - Get reminder details
- `PUT /api/v1/reminders/{id}` - Update reminder
- `DELETE /api/v1/reminders/{id}` - Delete reminder
- `POST /api/v1/reminders/{id}/complete` - Mark reminder as complete

#### Prescriptions
- `GET /api/v1/prescriptions` - List all prescriptions
- `POST /api/v1/prescriptions` - Create new prescription
- `GET /api/v1/prescriptions/{id}` - Get prescription details
- `PUT /api/v1/prescriptions/{id}` - Update prescription
- `DELETE /api/v1/prescriptions/{id}` - Delete prescription
- `GET /api/v1/prescriptions/{id}/image` - Get prescription image

#### Inventory
- `GET /api/v1/medicines/inventory/low` - Get low stock medicines
- `GET /api/v1/medicines/history` - Get inventory history

#### Notifications
- `GET /api/v1/notifications` - Get user notifications
- `PUT /api/v1/notifications/{id}/read` - Mark notification as read
- `DELETE /api/v1/notifications` - Clear all notifications

#### Search
- `GET /api/v1/search?q=query` - Universal search across all resources

#### Users
- `GET /api/v1/users/profile` - Get user profile
- `PUT /api/v1/users/profile` - Update profile
- `DELETE /api/v1/users/account` - Delete account
- `GET /api/v1/users/stats` - Get user statistics
- `POST /api/v1/users/export` - Export user data

## Database Schema

The application uses the following main tables:

- **users** - User accounts and profiles
- **medicines** - Medicine inventory and details
- **prescriptions** - Prescription documents and metadata
- **prescription_medicines** - Many-to-many relationship between prescriptions and medicines
- **reminders** - Medication reminders and scheduling
- **reminder_logs** - History of reminder completions
- **inventory_history** - Stock change history
- **notifications** - User notifications and alerts

## Security Features

- **Password Hashing**: Argon2 hashing for secure password storage
- **JWT Authentication**: Access and refresh token system
- **CORS Configuration**: Configurable cross-origin resource sharing
- **Input Validation**: Pydantic schemas for request validation
- **Error Handling**: Custom exception handling with appropriate HTTP status codes
- **File Validation**: Restricted file types and sizes for uploads

## Development Guidelines

### Adding New Features

1. Create a feature branch from main
2. Make your changes following the project structure
3. Add tests if applicable
4. Update documentation
5. Submit a pull request

## Deployment

### Frontend (Vercel/Netlify)

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Backend (Docker)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: pillio
      POSTGRES_USER: pillio_user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./pillio-backend
    environment:
      DATABASE_URL: postgresql+asyncpg://pillio_user:password@postgres:5432/pillio
      SECRET_KEY: your-secret-key
    ports:
      - "8000:8000"
    depends_on:
      - postgres

  frontend:
    build: .
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions, please open an issue in the repository or contact me!

## Acknowledgments

- [shadcn/ui](https://ui.shadcn.com/) for the beautiful component library
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent Python web framework
- [TanStack Query](https://tanstack.com/query) for powerful data fetching
- [Lucide](https://lucide.dev/) for the lovely icons
