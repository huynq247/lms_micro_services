#!/usr/bin/env python3
"""
Script to create a new MongoDB admin user
"""

from pymongo import MongoClient
from urllib.parse import quote_plus
import sys

def create_mongodb_user():
    try:
        # Current MongoDB connection with existing admin
        current_password = "Root@123"
        encoded_password = quote_plus(current_password)
        
        # Connect to MongoDB
        client = MongoClient(f"mongodb://admin:{encoded_password}@113.161.118.17:27017/admin")
        
        # Test connection
        admin_db = client.admin
        server_info = admin_db.command("ismaster")
        print(f"✅ Connected to MongoDB successfully")
        print(f"✅ Connection verified, proceeding to create user...")
        
        # Create new admin user
        new_username = "admin"
        new_password = "Mypassword123"
        
        # Check if user already exists
        existing_users = admin_db.command("usersInfo", new_username)
        if existing_users['users']:
            print(f"⚠️  User '{new_username}' already exists. Updating password...")
            
            # Update existing user password
            admin_db.command(
                "updateUser",
                new_username,
                pwd=new_password,
                roles=[
                    {"role": "userAdminAnyDatabase", "db": "admin"},
                    {"role": "readWriteAnyDatabase", "db": "admin"},
                    {"role": "dbAdminAnyDatabase", "db": "admin"},
                    {"role": "clusterAdmin", "db": "admin"}
                ]
            )
            print(f"✅ Updated password for user '{new_username}'")
        else:
            # Create new user
            admin_db.command(
                "createUser",
                new_username,
                pwd=new_password,
                roles=[
                    {"role": "userAdminAnyDatabase", "db": "admin"},
                    {"role": "readWriteAnyDatabase", "db": "admin"},
                    {"role": "dbAdminAnyDatabase", "db": "admin"},
                    {"role": "clusterAdmin", "db": "admin"}
                ]
            )
            print(f"✅ Created new admin user '{new_username}' successfully")
        
        # Test new credentials
        new_encoded_password = quote_plus(new_password)
        test_client = MongoClient(f"mongodb://{new_username}:{new_encoded_password}@113.161.118.17:27017/admin")
        test_admin_db = test_client.admin
        test_result = test_admin_db.command("ismaster")
        print(f"✅ New credentials verified successfully")
        
        # Show connection string
        print(f"\n📋 New MongoDB connection string:")
        print(f"MONGODB_URL=mongodb://{new_username}:{new_encoded_password}@113.161.118.17:27017")
        
        # Create content_db if it doesn't exist
        content_db = test_client.content_db
        # Create a test collection to initialize the database
        test_collection = content_db.test_collection
        test_collection.insert_one({"test": "initialization"})
        test_collection.delete_one({"test": "initialization"})
        print(f"✅ Database 'content_db' initialized")
        
        # List all databases
        print(f"\n📂 Available databases:")
        for db_name in test_client.list_database_names():
            print(f"  - {db_name}")
            
        client.close()
        test_client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    create_mongodb_user()
