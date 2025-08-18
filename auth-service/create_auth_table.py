#!/usr/bin/env python3
"""
Create auth_users table in PostgreSQL database
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_auth_table():
    """Create users table in mydb database"""
    
    # Database connection parameters
    db_params = {
        'host': 'localhost',
        'port': 25432,
        'user': 'admin',
        'password': 'Mypassword123',
        'database': 'mydb'
    }
    
    # SQL to create users table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        full_name VARCHAR(100),
        hashed_password VARCHAR(255) NOT NULL,
        role VARCHAR(20) DEFAULT 'STUDENT' NOT NULL,
        is_active BOOLEAN DEFAULT TRUE NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE,
        last_login TIMESTAMP WITH TIME ZONE
    );
    
    CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON users(username);
    CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);
    """
    
    try:
        # Connect to PostgreSQL
        print("🔗 Connecting to PostgreSQL...")
        conn = psycopg2.connect(**db_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Create cursor
        cursor = conn.cursor()
        
        # Execute table creation
        print("🛠️ Creating users table...")
        cursor.execute(create_table_sql)
        
        # Verify table creation
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("✅ Table 'users' created successfully!")
        print("📋 Table structure:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]} (nullable: {col[2]})")
            
        # Insert sample admin user
        print("\n👤 Creating admin user...")
        cursor.execute("""
            INSERT INTO users (username, email, full_name, hashed_password, role)
            VALUES ('admin', 'admin@lms.local', 'Administrator', 
                   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LwlAo/AgwpBqAiRWK', 'ADMIN')
            ON CONFLICT (username) DO NOTHING;
        """)
        
        print("✅ Admin user created (username: admin, password: secret)")
        
        # Close connections
        cursor.close()
        conn.close()
        
        print("🎉 Database setup completed!")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ PostgreSQL Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    create_auth_table()
