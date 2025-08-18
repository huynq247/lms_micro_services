#!/usr/bin/env python3
"""
Script to create the initial admin user for the Auth Service
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from app.core.database import engine, get_db
from app.utils.crud import UserCRUD
from app.schemas.user import UserCreate, UserRole

def create_admin_user():
    """Create initial admin user"""
    
    # Get database session
    db = next(get_db())
    user_crud = UserCRUD(db)
    
    # Check if admin user already exists
    existing_admin = user_crud.get_user_by_username("admin")
    if existing_admin:
        print("❌ Admin user already exists!")
        print(f"   Username: {existing_admin.username}")
        print(f"   Email: {existing_admin.email}")
        print(f"   Role: {existing_admin.role.value}")
        return
    
    # Create admin user
    admin_data = UserCreate(
        username="admin",
        email="admin@example.com",
        full_name="System Administrator",
        password="admin123456",  # Change this in production!
        role=UserRole.ADMIN,
        is_active=True
    )
    
    try:
        admin_user = user_crud.create_user(admin_data)
        print("✅ Admin user created successfully!")
        print(f"   Username: {admin_user.username}")
        print(f"   Email: {admin_user.email}")
        print(f"   Role: {admin_user.role.value}")
        print(f"   ID: {admin_user.id}")
        print()
        print("🔐 Default credentials:")
        print("   Username: admin")
        print("   Password: admin123456")
        print()
        print("⚠️  IMPORTANT: Change the admin password immediately in production!")
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
    finally:
        db.close()

def create_demo_users():
    """Create demo users for testing"""
    
    db = next(get_db())
    user_crud = UserCRUD(db)
    
    demo_users = [
        {
            "username": "teacher1",
            "email": "teacher1@example.com",
            "full_name": "John Teacher",
            "password": "teacher123",
            "role": UserRole.TEACHER
        },
        {
            "username": "student1",
            "email": "student1@example.com",
            "full_name": "Alice Student",
            "password": "student123",
            "role": UserRole.STUDENT
        },
        {
            "username": "student2",
            "email": "student2@example.com",
            "full_name": "Bob Student",
            "password": "student123",
            "role": UserRole.STUDENT
        }
    ]
    
    print("\n📚 Creating demo users...")
    
    for user_data in demo_users:
        existing_user = user_crud.get_user_by_username(user_data["username"])
        if existing_user:
            print(f"   ⚠️  User {user_data['username']} already exists, skipping...")
            continue
        
        try:
            user_create = UserCreate(**user_data)
            user = user_crud.create_user(user_create)
            print(f"   ✅ Created {user.role.value}: {user.username} ({user.email})")
        except Exception as e:
            print(f"   ❌ Error creating user {user_data['username']}: {e}")
    
    db.close()

if __name__ == "__main__":
    print("🚀 Setting up Auth Service users...")
    print("=" * 50)
    
    create_admin_user()
    
    # Ask if user wants to create demo users
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        create_demo_users()
    else:
        response = input("\n❓ Do you want to create demo users for testing? (y/n): ")
        if response.lower() in ['y', 'yes']:
            create_demo_users()
    
    print("\n🎉 User setup completed!")
    print("You can now start the Auth Service and test the API endpoints.")
