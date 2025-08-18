# LMS Role Matrix & Permissions

## 📋 **Role Definition**

### 🔐 **User Roles**
1. **ADMIN** - System Administrator 
2. **TEACHER** - Instructor/Teacher
3. **STUDENT** - Student/Learner

---

## 🗃️ **Permission Matrix**

### **Auth Service (Port 8001)**

| Endpoint | ADMIN | TEACHER | STUDENT | Notes |
|----------|--------|---------|---------|-------|
| `POST /api/v1/auth/login` | ✅ | ✅ | ✅ | All users can login |
| `POST /api/v1/auth/register` | ✅ | ✅ | ✅ | Public registration |
| `POST /api/v1/auth/refresh` | ✅ | ✅ | ✅ | Token refresh |
| `POST /api/v1/auth/logout` | ✅ | ✅ | ✅ | All users can logout |
| `GET /api/v1/auth/profile` | ✅ | ✅ | ✅ | Own profile only |
| `PUT /api/v1/auth/profile` | ✅ | ✅ | ✅ | Own profile only |
| `POST /api/v1/auth/reset-password` | ✅ | ✅ | ✅ | Password reset |
| **User Management** |
| `GET /api/v1/users` | ✅ | ❌ | ❌ | Admin only |
| `GET /api/v1/users/{id}` | ✅ | ❌ | ❌ | Admin only |
| `POST /api/v1/users` | ✅ | ❌ | ❌ | Admin only |
| `PUT /api/v1/users/{id}` | ✅ | ❌ | ❌ | Admin only |
| `DELETE /api/v1/users/{id}` | ✅ | ❌ | ❌ | Admin only |

### **Content Service (Port 8002)**

| Endpoint | ADMIN | TEACHER | STUDENT | Notes |
|----------|--------|---------|---------|-------|
| **Courses** |
| `GET /api/courses` | ✅ | ✅ | ✅ | View all courses |
| `POST /api/courses` | ✅ | ✅ | ❌ | Create courses |
| `PUT /api/courses/{id}` | ✅ | ✅ (own) | ❌ | Update own courses |
| `DELETE /api/courses/{id}` | ✅ | ✅ (own) | ❌ | Delete own courses |
| **Lessons** |
| `GET /api/courses/{id}/lessons` | ✅ | ✅ | ✅ | View lessons |
| `POST /api/courses/{id}/lessons` | ✅ | ✅ (own course) | ❌ | Create lessons |
| `PUT /api/lessons/{id}` | ✅ | ✅ (own) | ❌ | Update own lessons |
| `DELETE /api/lessons/{id}` | ✅ | ✅ (own) | ❌ | Delete own lessons |
| **Decks & Flashcards** |
| `GET /api/decks` | ✅ | ✅ | ✅ | View all decks |
| `POST /api/decks` | ✅ | ✅ | ❌ | Create decks |
| `PUT /api/decks/{id}` | ✅ | ✅ (own) | ❌ | Update own decks |
| `DELETE /api/decks/{id}` | ✅ | ✅ (own) | ❌ | Delete own decks |

### **Assignment Service (Port 8004)**

| Endpoint | ADMIN | TEACHER | STUDENT | Notes |
|----------|--------|---------|---------|-------|
| **Assignments** |
| `GET /api/assignments` | ✅ | ✅ (own) | ✅ (assigned) | View assignments |
| `POST /api/assignments` | ✅ | ✅ | ❌ | Create assignments |
| `PUT /api/assignments/{id}` | ✅ | ✅ (own) | ❌ | Update assignments |
| `DELETE /api/assignments/{id}` | ✅ | ✅ (own) | ❌ | Delete assignments |
| **Progress Tracking** |
| `GET /api/progress` | ✅ | ✅ (students) | ✅ (own) | View progress |
| `POST /api/progress` | ✅ | ❌ | ✅ | Submit progress |
| `PUT /api/progress/{id}` | ✅ | ✅ (grade) | ✅ (own) | Update progress |
| **Study Sessions** |
| `GET /api/sessions` | ✅ | ✅ (students) | ✅ (own) | View sessions |
| `POST /api/sessions` | ✅ | ❌ | ✅ | Create sessions |
| **Analytics** |
| `GET /api/analytics/summary` | ✅ | ✅ | ❌ | General analytics |
| `GET /api/analytics/instructors/{id}/dashboard` | ✅ | ✅ (own) | ❌ | Teacher dashboard |
| `GET /api/analytics/students/{id}/summary` | ✅ | ✅ (students) | ✅ (own) | Student progress |

---

## 🔧 **Frontend Role-Based Features**

### **Admin Dashboard**
- User management (CRUD operations)
- System analytics
- All courses and assignments overview
- System configuration

### **Teacher Dashboard**
- Course management (own courses)
- Assignment creation and management
- Student progress monitoring (enrolled students)
- Teaching analytics
- Deck and flashcard management

### **Student Dashboard**
- Enrolled courses view
- Assignment submissions
- Progress tracking (own progress)
- Study sessions
- Personal analytics

---

## 🔒 **Implementation Status**

### **Backend Permissions**
- ✅ Auth Service: Admin-only user management
- ✅ Basic role checking (admin vs non-admin)
- ⚠️ **NEED**: Teacher vs Student differentiation in Content/Assignment services
- ⚠️ **NEED**: Resource ownership checks (teachers can only edit own content)

### **Frontend Role Handling**
- ✅ Login/logout functionality
- ⚠️ **NEED**: Role-based navigation menus
- ⚠️ **NEED**: Conditional component rendering based on roles
- ⚠️ **NEED**: Route protection based on permissions

---

## 🎯 **Next Steps for Role Implementation**

### **1. Backend Enhancements**
```python
# Add role dependencies for teachers
def get_teacher_user(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Teacher privileges required")
    return current_user

# Add resource ownership checks
def check_course_ownership(course_id: int, current_user: User):
    # Verify teacher owns the course or is admin
    pass
```

### **2. Frontend Role Context**
```typescript
// AuthContext with role checking
interface AuthContextType {
  user: User | null;
  isAdmin: () => boolean;
  isTeacher: () => boolean;
  isStudent: () => boolean;
  hasPermission: (permission: string) => boolean;
}
```

### **3. Route Protection**
```typescript
// Protected routes based on roles
<ProtectedRoute requiredRole="TEACHER">
  <TeacherDashboard />
</ProtectedRoute>
```

---

## 📊 **Test Accounts Created**

| Username | Password | Role | Email | Full Name |
|----------|----------|------|-------|-----------|
| `admin` | `admin123456` | ADMIN | admin@example.com | System Admin |
| `teacher_demo` | `teacher123456` | TEACHER | teacher.demo@example.com | Teacher Demo |
| `student_demo` | `student123456` | STUDENT | student.demo@example.com | Student Demo |

---

## 🔍 **Permission Testing Checklist**

### **Authentication Tests**
- [ ] All users can login/logout
- [ ] Token refresh works for all roles
- [ ] Profile access works for all users

### **Admin Tests**
- [ ] Can access user management endpoints
- [ ] Can view all system data
- [ ] Can create/edit/delete any resource

### **Teacher Tests**
- [ ] Can create courses and assignments
- [ ] Can only edit own content
- [ ] Can view assigned students' progress
- [ ] Cannot access admin functions

### **Student Tests**
- [ ] Can view assigned content
- [ ] Can submit assignments
- [ ] Can track own progress
- [ ] Cannot access teacher/admin functions
