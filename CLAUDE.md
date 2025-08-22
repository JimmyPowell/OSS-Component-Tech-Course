# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a comprehensive educational platform built with FastAPI backend and Vue.js frontends. It includes:
- Course resource management (PPTs, videos, attachments)
- Homework assignment system
- Student showcase and portfolio features
- Forum discussion system (backend implemented, frontend in progress)
- Separate admin panel for content management

## Architecture

### Backend (FastAPI)
- **Location**: `backend/`
- **Main entry**: `backend/app/main.py`
- **Architecture pattern**: Clean architecture with separation of concerns
- **Key layers**:
  - `models/` - SQLAlchemy ORM models
  - `schemas/` - Pydantic schemas for API validation
  - `crud/` - Database operations layer
  - `api/endpoints/` - API route handlers
  - `services/` - Business logic services
  - `config/` - Database and application configuration

### Frontend (Vue 3)
Two separate Vue.js applications:
1. **User Frontend** (`frontend/`):
   - Main educational platform interface
   - Uses Vue 3 + Vite + Pinia + Bootstrap
   - Ports: dev=5173, preview=5174

2. **Admin Frontend** (`frontend-admin/`):
   - Administrative interface
   - Uses Vue 3 + Vite + Ant Design Vue
   - Ports: dev=5173, preview=5174

### Database
- **Primary**: MySQL with SQLAlchemy ORM
- **Cache**: Redis for JWT blacklisting and caching
- **Schema**: `sql/schema.sql`

## Development Commands

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (User)
```bash
cd frontend
npm install
npm run dev      # Development server
npm run build    # Production build
npm run preview  # Preview built app
```

### Frontend Admin
```bash
cd frontend-admin
npm install
npm run dev      # Development server
npm run build    # Production build  
npm run preview  # Preview built app
```

## Configuration
- Backend config via environment variables (see `backend/app/config/settings.py`)
- Required .env file in `backend/` directory with:
  - MySQL credentials
  - Redis connection
  - JWT secrets
  - Email service settings
  - Qiniu cloud storage keys

## API Structure
- Base URL: `/api/v1`
- Authentication: JWT Bearer tokens
- Key endpoints:
  - `/auth` - User authentication
  - `/course-resources` - Course materials
  - `/homeworks` - Assignment management
  - `/showcases` - Student work portfolios
  - `/forum` - Discussion system
  - `/admin/*` - Administrative functions

## Database Models
Core entities include:
- `User` - User accounts with role-based permissions
- `CourseResource` - Educational materials (PPT, video, attachments)
- `Homework` - Assignments and submissions
- `Showcase` - Student portfolio items with comments/replies
- `ForumCategory/Post/Reply` - Discussion forum system
- Like system for showcases and comments

## Key Features
- JWT-based authentication with refresh tokens
- Role-based access control (user/manager)
- File upload via Qiniu cloud storage
- Email verification system
- Soft delete pattern for most entities
- Rich text content support
- Comment and reply threading
- Like/unlike functionality

## Current Development Status
- Backend: Fully implemented including forum system
- User Frontend: Core features implemented, forum UI pending
- Admin Frontend: Management interfaces for all content types
- Database: Complete schema with all relationships

## Notes for Development
- Follow the existing CRUD pattern when adding new features
- All API endpoints should include proper error handling via `app.utils.response`
- Use UUID fields for public-facing identifiers
- Implement proper authorization checks using dependencies in `app.api.deps`
- Frontend state management uses Pinia stores
- Both frontends use Vite for build tooling


## user's notes
- No need to start the frontend or backend server,as user has started
- When it comes to the frontend modification,use the playwright to review
