#!/usr/bin/env python3
"""
Database initialization script for Assignment Service
"""

import asyncio
import asyncpg
from datetime import datetime

async def create_database_schema():
    """Create database schema and tables"""
    
    # Connection settings
    connection_params = {
        'host': '113.161.118.17',
        'port': 25432,
        'user': 'admin',
        'password': 'Mypassword123',
        'database': 'assignment_db'
    }
    
    try:
        # Connect to PostgreSQL
        conn = await asyncpg.connect(**connection_params)
        print("✅ Connected to PostgreSQL successfully")
        
        # Create assignments table
        await conn.execute("""
            DROP TABLE IF EXISTS study_sessions CASCADE;
            DROP TABLE IF EXISTS progress CASCADE; 
            DROP TABLE IF EXISTS assignments CASCADE;
            
            CREATE TABLE assignments (
                id SERIAL PRIMARY KEY,
                instructor_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                content_type VARCHAR(20) NOT NULL CHECK (content_type IN ('course', 'deck')),
                content_id VARCHAR(24) NOT NULL,
                content_title VARCHAR(200) NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                instructions TEXT,
                assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                due_date TIMESTAMP WITH TIME ZONE,
                completed_at TIMESTAMP WITH TIME ZONE,
                status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'overdue')),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE
            );
        """)
        
        print("✅ Created assignments table")
        
        # Create progress table
        await conn.execute("""
            CREATE TABLE progress (
                id SERIAL PRIMARY KEY,
                assignment_id INTEGER NOT NULL UNIQUE,
                total_items INTEGER DEFAULT 0,
                completed_items INTEGER DEFAULT 0,
                completion_percentage REAL DEFAULT 0.0,
                total_study_time_minutes INTEGER DEFAULT 0,
                sessions_count INTEGER DEFAULT 0,
                started_at TIMESTAMP WITH TIME ZONE,
                last_accessed TIMESTAMP WITH TIME ZONE,
                progress_details TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE,
                FOREIGN KEY (assignment_id) REFERENCES assignments(id) ON DELETE CASCADE
            );
        """)
        
        print("✅ Created progress table")
        
        # Create study_sessions table
        await conn.execute("""
            CREATE TABLE study_sessions (
                id SERIAL PRIMARY KEY,
                assignment_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                ended_at TIMESTAMP WITH TIME ZONE,
                duration_minutes INTEGER,
                items_studied INTEGER DEFAULT 0,
                items_completed INTEGER DEFAULT 0,
                session_progress REAL DEFAULT 0.0,
                session_notes TEXT,
                items_details TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE,
                FOREIGN KEY (assignment_id) REFERENCES assignments(id) ON DELETE CASCADE
            );
        """)
        
        print("✅ Created study_sessions table")
        
        # Create indexes
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_assignments_instructor ON assignments(instructor_id);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_assignments_student ON assignments(student_id);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_assignments_status ON assignments(status);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_study_sessions_assignment ON study_sessions(assignment_id);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_study_sessions_student ON study_sessions(student_id);")
        
        print("✅ Created indexes")
        
        # Insert sample data
        await conn.execute("""
            INSERT INTO assignments (instructor_id, student_id, content_type, content_id, content_title, title, description)
            VALUES 
                (1, 3, 'course', '689ea5ac55048890040b7aa6', 'Python Programming Fundamentals', 'Complete Python Course', 'Study all lessons in the Python course'),
                (1, 4, 'deck', '689ea5b255048890040b7aa8', 'Python Vocabulary', 'Learn Python Terms', 'Study all flashcards about Python terminology')
            ON CONFLICT DO NOTHING;
        """)
        
        print("✅ Inserted sample assignments")
        
        # Create progress records for assignments
        await conn.execute("""
            INSERT INTO progress (assignment_id, total_items, completed_items, completion_percentage)
            SELECT id, 10, 0, 0.0 FROM assignments
            ON CONFLICT (assignment_id) DO NOTHING;
        """)
        
        print("✅ Created initial progress records")
        
        # Show tables
        result = await conn.fetch("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        print(f"\n📋 Database tables created:")
        for row in result:
            print(f"  - {row['table_name']}")
            
        # Show assignment count
        count = await conn.fetchval("SELECT COUNT(*) FROM assignments")
        print(f"\n📊 Sample data: {count} assignments created")
        
        await conn.close()
        print("\n🎉 Database schema created successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(create_database_schema())
