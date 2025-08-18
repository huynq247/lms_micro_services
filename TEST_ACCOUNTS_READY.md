# 🧪 Test Accounts for LMS System

## 📅 Created: August 18, 2025
## 🎯 Purpose: Frontend & Backend Testing with Role-Based Features

---

## 🔐 Available Test Accounts

### 👨‍💼 **ADMIN Account**
```
Username: admin
Password: admin123456
Email: admin@lms.local
Role: ADMIN
Full Name: System Administrator
```

**Admin Capabilities:**
- ✅ Full system access
- ✅ User management (create, edit, delete users)
- ✅ System-wide analytics dashboard
- ✅ Assignment management
- ✅ Course management
- ✅ All student and teacher features

---

### 👨‍🏫 **TEACHER Accounts**

#### Teacher 1
```
Username: teacher_demo
Password: teacher123456
Email: teacher.demo@example.com
Role: TEACHER
Full Name: Teacher Demo
```

#### Teacher 2 (if created)
```
Username: teacher2
Password: teacher123456
Email: teacher2@example.com
Role: TEACHER
Full Name: Teacher Two
```

**Teacher Capabilities:**
- ✅ Create and manage assignments
- ✅ View student progress
- ✅ Class analytics dashboard
- ✅ Course content management
- ✅ Student performance tracking
- ❌ User management (Admin only)
- ❌ System-wide analytics (Admin only)

---

### 👨‍🎓 **STUDENT Accounts**

#### Student Demo
```
Username: student_demo
Password: student123456
Email: student.demo@example.com
Role: STUDENT
Full Name: Student Demo
```

**Student Capabilities:**
- ✅ View assigned courses
- ✅ Submit assignments
- ✅ Track personal progress
- ✅ View personal analytics
- ❌ Create assignments (Teacher/Admin only)
- ❌ User management (Admin only)
- ❌ System analytics (Teacher/Admin only)

---

## 🔗 Frontend Testing URLs

### Access Points:
- **Frontend:** http://localhost:3000
- **API Gateway:** http://localhost:8000
- **Direct Auth Service:** http://localhost:8001
- **Content Service:** http://localhost:8002
- **Assignment Service:** http://localhost:8004

### Frontend Routes by Role:

#### **All Users:**
- `/dashboard` - Role-specific dashboard
- `/courses` - Course browsing
- `/assignments` - Assignment management

#### **Teacher + Admin Only:**
- `/analytics` - Analytics dashboard

#### **Admin Only:**
- `/users` - User management

---

## 🧪 Testing Scenarios

### 1. **Login Flow Testing**
```bash
# Test each account login
1. Go to http://localhost:3000/login
2. Try each username/password combination
3. Verify role-based redirect and dashboard content
```

### 2. **Role-Based Navigation Testing**
```bash
# Admin should see all menu items:
- Dashboard, Courses, Assignments, User Management, Analytics

# Teacher should see:
- Dashboard, Courses, Assignments, Analytics

# Student should see:
- Dashboard, Courses, Assignments
```

### 3. **Feature Access Testing**
```bash
# Test role restrictions:
1. Login as STUDENT → try to access /users → should show "Access denied"
2. Login as TEACHER → try to access /users → should show "Access denied"
3. Login as ADMIN → access /users → should show user management interface
```

### 4. **API Integration Testing**
```bash
# Test API calls through API Gateway:
1. Login → verify JWT token storage
2. Dashboard → verify analytics data loading
3. Assignments → verify CRUD operations (role-dependent)
```

---

## 🚀 Quick Test Commands

### Test Authentication:
```powershell
# Login as Admin
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"username":"admin","password":"admin123456"}'

# Login as Teacher
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"username":"teacher_demo","password":"teacher123456"}'

# Login as Student
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"username":"student_demo","password":"student123456"}'
```

### Test Analytics:
```powershell
curl http://localhost:8000/api/analytics/summary
```

### Test Assignments:
```powershell
curl "http://localhost:8000/api/assignments/?page=1&size=10"
```

---

## 📊 Expected Behavior

### **Dashboard Content by Role:**

| Feature | Student | Teacher | Admin |
|---------|---------|---------|-------|
| Personal Stats | ✅ | ✅ | ✅ |
| Class Overview | ❌ | ✅ | ✅ |
| System Stats | ❌ | ❌ | ✅ |
| User Count | ❌ | ❌ | ✅ |

### **Assignment Features:**

| Action | Student | Teacher | Admin |
|---------|---------|---------|-------|
| View Assignments | ✅ | ✅ | ✅ |
| Create Assignment | ❌ | ✅ | ✅ |
| Edit Assignment | ❌ | ✅ (own) | ✅ (all) |
| Delete Assignment | ❌ | ✅ (own) | ✅ (all) |

---

## 🔧 Troubleshooting

### **Common Issues:**
1. **404 on login** → Check API Gateway is running on port 8000
2. **Frontend compilation errors** → Check all role-based components imported correctly
3. **Access denied errors** → Verify JWT token and role in browser storage
4. **Analytics not loading** → Check assignment service running on port 8004

### **Service Status Check:**
```powershell
netstat -ano | findstr ":3000.*LISTENING"  # Frontend
netstat -ano | findstr ":8000.*LISTENING"  # API Gateway
netstat -ano | findstr ":8001.*LISTENING"  # Auth Service
netstat -ano | findstr ":8002.*LISTENING"  # Content Service
netstat -ano | findstr ":8004.*LISTENING"  # Assignment Service
```

---

## 🎯 Testing Checklist

- [ ] All accounts can login successfully
- [ ] Role-based navigation shows correct menu items
- [ ] Admin can access user management
- [ ] Teacher can create assignments
- [ ] Student can view assignments but not create
- [ ] Analytics page shows role-appropriate data
- [ ] Access restrictions work properly
- [ ] API Gateway routes all requests correctly

---

**🎉 Ready for comprehensive frontend and backend testing!**
