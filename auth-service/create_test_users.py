#!/usr/bin/env python3
"""
Create test users for LMS system
- Teachers and Students accounts
- Save credentials to text file for testing
"""

import asyncio
import asyncpg
import bcrypt
from datetime import datetime
import json

DATABASE_URL = "postgresql://lms_user:lms_password@localhost:5432/lms_auth"

# Test users data
TEST_USERS = [
    # Teachers
    {
        "username": "teacher1",
        "email": "teacher1@lms.local", 
        "password": "teacher123",
        "full_name": "Nguyễn Văn Giáo",
        "role": "teacher",
        "is_active": True
    },
    {
        "username": "teacher2", 
        "email": "teacher2@lms.local",
        "password": "teacher456",
        "full_name": "Trần Thị Hương", 
        "role": "teacher",
        "is_active": True
    },
    {
        "username": "teacher3",
        "email": "teacher3@lms.local",
        "password": "teacher789", 
        "full_name": "Lê Minh Tuấn",
        "role": "teacher",
        "is_active": True
    },
    
    # Students
    {
        "username": "student1",
        "email": "student1@lms.local",
        "password": "student123", 
        "full_name": "Phạm Văn An",
        "role": "student",
        "is_active": True
    },
    {
        "username": "student2",
        "email": "student2@lms.local", 
        "password": "student456",
        "full_name": "Ngô Thị Bình",
        "role": "student", 
        "is_active": True
    },
    {
        "username": "student3",
        "email": "student3@lms.local",
        "password": "student789",
        "full_name": "Hoàng Minh Cường", 
        "role": "student",
        "is_active": True
    },
    {
        "username": "student4",
        "email": "student4@lms.local",
        "password": "student101",
        "full_name": "Vũ Thị Dung",
        "role": "student",
        "is_active": True
    },
    {
        "username": "student5", 
        "email": "student5@lms.local",
        "password": "student202",
        "full_name": "Đặng Văn Định",
        "role": "student",
        "is_active": True
    }
]

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

async def create_test_users():
    """Create test users in database"""
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        print("🔄 Creating test users...")
        created_users = []
        
        for user_data in TEST_USERS:
            # Check if user exists
            existing = await conn.fetchrow(
                "SELECT id FROM users WHERE username = $1 OR email = $2",
                user_data["username"], user_data["email"]
            )
            
            if existing:
                print(f"⚠️  User {user_data['username']} already exists, skipping...")
                continue
            
            # Hash password
            hashed_password = hash_password(user_data["password"])
            
            # Insert user
            user_id = await conn.fetchval(
                """
                INSERT INTO users (username, email, hashed_password, full_name, role, is_active, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
                """,
                user_data["username"],
                user_data["email"], 
                hashed_password,
                user_data["full_name"],
                user_data["role"],
                user_data["is_active"],
                datetime.utcnow(),
                datetime.utcnow()
            )
            
            created_user = {
                "id": user_id,
                "username": user_data["username"],
                "email": user_data["email"],
                "password": user_data["password"],  # Plain password for testing
                "full_name": user_data["full_name"], 
                "role": user_data["role"],
                "is_active": user_data["is_active"]
            }
            
            created_users.append(created_user)
            print(f"✅ Created {user_data['role']}: {user_data['username']} (ID: {user_id})")
        
        print(f"\n🎉 Successfully created {len(created_users)} users!")
        return created_users
        
    except Exception as e:
        print(f"❌ Error creating users: {e}")
        return []
    finally:
        await conn.close()

async def save_credentials_to_file(users):
    """Save user credentials to text file for testing"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_users_credentials_{timestamp}.txt"
    
    content = f"""
# LMS Test Users Credentials
# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Database: {DATABASE_URL}

====================================
🧑‍🏫 TEACHERS ACCOUNTS
====================================
"""
    
    teachers = [u for u in users if u["role"] == "teacher"]
    for i, user in enumerate(teachers, 1):
        content += f"""
Teacher {i}:
  ID: {user['id']}
  Username: {user['username']}
  Email: {user['email']}
  Password: {user['password']}
  Full Name: {user['full_name']}
  Role: {user['role']}
  
  Login Command:
  curl -X POST "http://localhost:8000/api/v1/auth/login" \\
    -H "Content-Type: application/json" \\
    -d '{{"username":"{user['username']}","password":"{user['password']}"}}'
"""

    content += f"""

====================================
🎓 STUDENTS ACCOUNTS  
====================================
"""
    
    students = [u for u in users if u["role"] == "student"]
    for i, user in enumerate(students, 1):
        content += f"""
Student {i}:
  ID: {user['id']}
  Username: {user['username']}
  Email: {user['email']}
  Password: {user['password']}
  Full Name: {user['full_name']}
  Role: {user['role']}
  
  Login Command:
  curl -X POST "http://localhost:8000/api/v1/auth/login" \\
    -H "Content-Type: application/json" \\
    -d '{{"username":"{user['username']}","password":"{user['password']}"}}'
"""

    content += f"""

====================================
📊 SUMMARY
====================================
Total Users: {len(users)}
Teachers: {len(teachers)}
Students: {len(students)}

Frontend Login URL: http://localhost:3000/login
API Gateway URL: http://localhost:8000
Auth Service URL: http://localhost:8001

====================================
🧪 TESTING INSTRUCTIONS
====================================

1. Frontend Testing:
   - Go to http://localhost:3000/login
   - Use any username/password combination above
   - Test different roles (teacher vs student)

2. API Testing:
   - Use the curl commands above
   - Or test via Postman/Insomnia
   - Check JWT token response

3. Role-based Testing:
   - Teachers should have access to create assignments
   - Students should only see assigned content
   - Test permissions and role restrictions

====================================
🔐 SECURITY NOTE
====================================
These are TEST CREDENTIALS only!
Do not use in production environment.
Change all passwords before going live.
"""

    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"📝 Credentials saved to: {filename}")
    return filename

async def main():
    """Main function"""
    print("🚀 LMS Test Users Creation Script")
    print("=" * 50)
    
    # Create users
    users = await create_test_users()
    
    if users:
        # Save credentials
        credentials_file = await save_credentials_to_file(users)
        print(f"\n✅ Process completed!")
        print(f"📁 Credentials file: {credentials_file}")
        print(f"🌐 Frontend URL: http://localhost:3000/login")
        print(f"🔗 API Gateway: http://localhost:8000")
    else:
        print("❌ No users were created")

if __name__ == "__main__":
    asyncio.run(main())
