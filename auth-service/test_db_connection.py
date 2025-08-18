"""
Test PostgreSQL connection and create auth_users table
"""
import psycopg2
from psycopg2 import sql
import sys

# Database connection parameters
DB_CONFIG = {
    'host': '113.161.118.17',
    'port': 25432,
    'user': 'admin',
    'password': 'Mypassword123',
    'database': 'postgres'
}

def test_connection():
    """Test PostgreSQL connection"""
    try:
        print("🔄 Testing PostgreSQL connection...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connected successfully!")
        print(f"📊 PostgreSQL version: {version[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def create_auth_table():
    """Create auth_users table if not exists"""
    try:
        print("🔄 Creating auth_users table...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Create auth_users table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS auth_users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        
        print("✅ Table 'auth_users' created successfully!")
        
        # Check if table exists
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'auth_users';
        """)
        
        columns = cursor.fetchall()
        print("📋 Table structure:")
        for col_name, col_type in columns:
            print(f"  - {col_name}: {col_type}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create table: {e}")
        return False

def main():
    print("🚀 Auth Service Database Setup")
    print("=" * 40)
    
    # Test connection
    if not test_connection():
        print("❌ Cannot connect to database. Please check:")
        print("  - Network connectivity to 113.161.118.17:25432")
        print("  - PostgreSQL server is running")
        print("  - Credentials are correct")
        print("  - Firewall allows connection")
        sys.exit(1)
    
    # Create table
    if create_auth_table():
        print("\n🎉 Database setup completed successfully!")
        print("🚀 You can now start the auth-service:")
        print("   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload")
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
