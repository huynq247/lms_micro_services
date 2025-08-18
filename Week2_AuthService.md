# 🔐 WEEK 2: AUTH SERVICE

**Focus**: Authentication & Authorization Service
**Timeline**: Week 2 (7 days)
**Port**: 8001
**Database**: PostgreSQL

---

## 🏗️ PROJECT STRUCTURE

### FastAPI Setup
- [x] Create auth-service directory
- [x] Setup FastAPI project structure
- [x] Configure PostgreSQL connection
- [x] Setup Alembic for migrations
- [x] Create base models and schemas

### Directory Structure
```
auth-service/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   ├── schemas/
│   ├── api/
│   ├── core/
│   └── utils/
├── alembic/
├── requirements.txt
└── Dockerfile
```

---

## 🗄️ DATABASE SCHEMA

### Tables Design
- [x] Users table (id, email, username, password_hash, role, created_at, updated_at)
- [x] Tokens table (id, user_id, token, token_type, expires_at, is_revoked)
- [x] Create initial migration
- [x] Seed admin user

### User Roles
- **Admin**: System administrator
- **Instructor**: Creates content and manages students
- **Student**: Consumes assigned content

---

## 🔑 CORE FEATURES

### Authentication Endpoints
- [x] User registration endpoint
- [x] User login endpoint (JWT generation)
- [x] Token refresh endpoint
- [x] User logout endpoint (token blacklisting)
- [ ] Password reset request endpoint
- [ ] Password reset confirm endpoint
- [x] Get user profile endpoint
- [x] Update user profile endpoint

### Admin Features
- [x] Create instructor endpoint (admin only)
- [x] List users endpoint (admin only)
- [x] Deactivate user endpoint (admin only)

### Instructor Features
- [ ] Create student endpoint (instructor only)
- [ ] List students endpoint (instructor only)

---

## 🔒 SECURITY & VALIDATION

### Security Implementation
- [x] JWT token generation and validation
- [x] Password hashing with bcrypt
- [x] Role-based access control middleware
- [ ] Request rate limiting
- [x] Input validation with Pydantic
- [x] CORS configuration

### Middleware
- [x] Authentication middleware
- [x] Authorization middleware
- [ ] Rate limiting middleware
- [ ] Request logging middleware

---

## 🧪 TESTING

### Test Coverage
- [ ] Unit tests for authentication logic
- [ ] Integration tests for endpoints
- [ ] Test JWT token flows
- [ ] Test role-based access
- [ ] Test password hashing/verification
- [ ] Test rate limiting

### Test Data
- [ ] Create test users for each role
- [ ] Test token scenarios
- [ ] Test error cases

---

## 📊 API ENDPOINTS (8 total)

```yaml
POST /auth/register
POST /auth/login
POST /auth/refresh
POST /auth/logout
GET /auth/profile
PUT /auth/profile
POST /admin/users/instructor
GET /admin/users
```

---

## ✅ WEEK 2 COMPLETION CRITERIA

- [x] Auth service running on port 8001
- [x] All 8 endpoints implemented and tested
- [x] JWT authentication working
- [x] Role-based access control functional
- [x] Database migrations applied
- [x] Admin user seeded

**Status: ✅ COMPLETED - Ready for Content Service**

Tiếp:
Tạo Content Service (MongoDB + FastAPI)
Thiết lập API Gateway (Traefik) -API Gateway Traefik (Week 7) - LÀM CUỐI