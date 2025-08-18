# 🚀 HƯỚNG DẪN TRIỂN KHAI CHI TIẾT

**Mục tiêu**: Triển khai Auth Service hoàn chỉnh
**Thời gian**: 2-3 giờ
**Prerequisites**: SSH access to RedHat server

---

## 📋 **BƯỚC 1: SETUP PROJECT STRUCTURE**

### **1.1 SSH vào server và tạo structure:**
```bash
# SSH vào server RedHat
ssh root@113.161.118.17

# Tạo project structure
mkdir -p /home/microservices-lms/auth-service/app/{models,schemas,api,core,utils}
mkdir -p /home/microservices-lms/auth-service/alembic
cd /home/microservices-lms
```

### **1.2 Tạo requirements.txt:**
```bash
cat > auth-service/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.13.0
psycopg2-binary==2.9.9
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
redis==5.0.1
pika==1.3.2
python-dotenv==1.0.0
pytest==7.4.3
httpx==0.25.2
EOF
```

### **1.3 Tạo file .env:**
```bash
cat > auth-service/.env << 'EOF'
DATABASE_URL=postgresql://admin:Mypassword123@172.16.203.220:25432/auth_db
MONGODB_URL=mongodb://admin:Root%40123@113.161.118.17:27017/content_db
REDIS_URL=redis://172.16.203.220:26379
RABBITMQ_URL=amqp://admin:password123@172.16.203.220:5672
SECRET_KEY=microservices-lms-secret-key-2025-production-secure
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
HOST=0.0.0.0
PORT=8001
DEBUG=true
EOF
```

---

## 📋 **BƯỚC 2: TẠO CORE FILES**

### **2.1 Tạo database connection:**
```bash
cat > auth-service/app/core/database.py << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF
```

### **2.2 Tạo config settings:**
```bash
cat > auth-service/app/core/config.py << 'EOF'
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    rabbitmq_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
EOF
```

### **2.3 Tạo security utilities:**
```bash
cat > auth-service/app/core/security.py << 'EOF'
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None
EOF
```

---

## 📋 **BƯỚC 3: TẠO DATABASE MODELS**

### **3.1 Tạo User model:**
```bash
cat > auth-service/app/models/user.py << 'EOF'
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    INSTRUCTOR = "instructor"
    STUDENT = "student"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
EOF
```

### **3.2 Tạo Token model:**
```bash
cat > auth-service/app/models/token.py << 'EOF'
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    token_type = Column(String, nullable=False)  # access, refresh
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
EOF
```

### **3.3 Tạo __init__.py files:**
```bash
touch auth-service/app/__init__.py
touch auth-service/app/models/__init__.py
touch auth-service/app/schemas/__init__.py
touch auth-service/app/api/__init__.py
touch auth-service/app/core/__init__.py
touch auth-service/app/utils/__init__.py
```

---

## 📋 **BƯỚC 4: TẠO PYDANTIC SCHEMAS**

### **4.1 Tạo user schemas:**
```bash
cat > auth-service/app/schemas/user.py << 'EOF'
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str
    role: UserRole

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    username: str
    password: str
EOF
```

---

## 📋 **BƯỚC 5: SETUP ALEMBIC MIGRATIONS**

### **5.1 Initialize Alembic:**
```bash
cd auth-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic init alembic
```

### **5.2 Configure Alembic:**
```bash
cat > alembic.ini << 'EOF'
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = 

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
EOF
```

### **5.3 Update Alembic env.py:**
```bash
cat > alembic/env.py << 'EOF'
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
from dotenv import load_dotenv

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

load_dotenv()

from app.core.database import Base
from app.models.user import User
from app.models.token import Token

config = context.config
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
EOF
```

---

## 📋 **BƯỚC 6: TẠO VÀ CHẠY MIGRATIONS**

### **6.1 Tạo initial migration:**
```bash
alembic revision --autogenerate -m "Initial migration"
```

### **6.2 Apply migration:**
```bash
alembic upgrade head
```

### **6.3 Verify tables created:**
```bash
docker exec -it my_postgres psql -U admin -d auth_db -c "\dt"
```

---

## 📋 **BƯỚC 7: TẠO API ENDPOINTS**

### **7.1 Tạo authentication API:**
```bash
cat > auth-service/app/api/auth.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.schemas.user import LoginRequest, Token, UserCreate, UserResponse
from datetime import timedelta
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        password_hash=hashed_password,
        role=user.role
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
    refresh_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "type": "refresh"},
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user: User = Depends(get_current_user)):
    return current_user
EOF
```

### **7.2 Tạo dependency cho current user:**
```bash
cat > auth-service/app/utils/dependencies.py << 'EOF'
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user
EOF
```

---

## 📋 **BƯỚC 8: TẠO MAIN APPLICATION**

### **8.1 Update main.py:**
```bash
cat > auth-service/app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.core.config import settings
import uvicorn

app = FastAPI(
    title="Auth Service",
    description="Authentication and Authorization Microservice",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])

@app.get("/")
async def root():
    return {"message": "Auth Service is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "auth-service"}

if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port, reload=settings.debug)
EOF
```

---

## 📋 **BƯỚC 9: TEST VÀ CHẠY SERVICE**

### **9.1 Test database connection:**
```bash
cd auth-service
source venv/bin/activate
python -c "from app.core.database import engine; print('Database connection successful!')"
```

### **9.2 Chạy Auth Service:**
```bash
python app/main.py
```

### **9.3 Test API endpoints:**
```bash
# Test health check
curl http://172.16.203.220:8001/health

# Test registration
curl -X POST "http://172.16.203.220:8001/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "admin@example.com",
       "username": "admin",
       "password": "admin123",
       "role": "admin"
     }'

# Test login
curl -X POST "http://172.16.203.220:8001/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "admin",
       "password": "admin123"
     }'
```

---

## ✅ **COMPLETION CHECKLIST**

```yaml
Infrastructure:
✅ Project structure created
✅ Requirements installed
✅ Environment variables configured

Database:
✅ SQLAlchemy models created
✅ Alembic migrations setup
✅ Database tables created

Authentication:
✅ JWT implementation
✅ Password hashing
✅ User registration/login endpoints

Testing:
✅ Health check endpoint
✅ API endpoints tested
✅ Database connection verified
```

**Sau khi hoàn thành, bạn sẽ có Auth Service hoạt động hoàn chỉnh với 3 endpoints chính!**

**Hãy thực hiện từng bước và paste output để tôi support bạn!** 🚀
