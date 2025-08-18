# 🏗️ FLEXIBLE DATABASE ARCHITECTURE DESIGN

**Mục tiêu**: Thiết kế cấu hình linh hoạt cho single server → distributed architecture
**Principle**: Zero code change khi migrate
**Date**: 14/08/2025

---

## 🎯 **DESIGN PHILOSOPHY**

### **Core Principles:**
```yaml
Environment-Based Configuration:
✅ Tất cả connection strings trong environment variables
✅ Không hardcode database URLs trong code
✅ Service discovery ready
✅ Container orchestration ready

Database Per Service:
✅ Auth Service → PostgreSQL instance
✅ Content Service → MongoDB instance  
✅ Assignment Service → PostgreSQL instance
✅ Shared services → Redis, RabbitMQ
```

---

## 📋 **CURRENT SETUP (SINGLE SERVER)**

### **Environment Structure:**
```bash
# Current .env structure
cat > auth-service/.env << 'EOF'
# === DATABASE CONFIGURATION ===
# Primary database for this service
DATABASE_URL=postgresql://admin:Mypassword123@172.16.203.220:25432/auth_db

# === SHARED SERVICES ===
# Cache layer
REDIS_URL=redis://172.16.203.220:26379
# Message queue
RABBITMQ_URL=amqp://admin:password123@172.16.203.220:5672

# === CROSS-SERVICE COMMUNICATION ===
# Content service database (for future integration)
CONTENT_DB_URL=mongodb://admin:Root%40123@113.161.118.17:27017/content_db
# Assignment service database (for future integration)
ASSIGNMENT_DB_URL=postgresql://admin:Mypassword123@172.16.203.220:25432/assignment_db

# === SERVICE DISCOVERY ===
# Current server info
LOCAL_IP=172.16.203.220
PUBLIC_IP=113.161.118.17
SERVICE_NAME=auth-service
SERVICE_PORT=8001

# === ENVIRONMENT ===
ENVIRONMENT=development
DEPLOYMENT_TYPE=single-server
EOF
```

---

## 🔄 **FLEXIBLE CONFIGURATION SYSTEM**

### **1. Multi-Environment Config Class:**
```python
# auth-service/app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any
import os

class DatabaseConfig(BaseSettings):
    """Database configuration with fallback options"""
    
    # Primary database
    database_url: str
    
    # Connection pool settings
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    
    # Failover options (for future)
    read_replica_urls: Optional[list] = None
    write_replica_url: Optional[str] = None

class SharedServicesConfig(BaseSettings):
    """Shared services configuration"""
    
    # Cache
    redis_url: str
    redis_cluster_urls: Optional[list] = None
    
    # Message queue
    rabbitmq_url: str
    rabbitmq_cluster_urls: Optional[list] = None

class ServiceDiscoveryConfig(BaseSettings):
    """Service discovery configuration"""
    
    # Current service info
    service_name: str = "auth-service"
    service_port: int = 8001
    local_ip: str
    public_ip: str
    
    # Other services (for future communication)
    content_service_url: Optional[str] = None
    assignment_service_url: Optional[str] = None
    
    # Load balancer/gateway
    api_gateway_url: Optional[str] = None

class Settings(BaseSettings):
    """Main application settings"""
    
    # Environment
    environment: str = "development"
    deployment_type: str = "single-server"  # single-server, distributed, kubernetes
    
    # Database config
    db: DatabaseConfig
    
    # Shared services
    shared: SharedServicesConfig
    
    # Service discovery
    discovery: ServiceDiscoveryConfig
    
    # JWT settings
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Application settings
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = True
    
    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"

# Factory function for different environments
def get_settings() -> Settings:
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "development":
        return Settings()
    elif env == "staging":
        return StagingSettings()
    elif env == "production":
        return ProductionSettings()
    else:
        return Settings()

settings = get_settings()
```

### **2. Dynamic Database Connection:**
```python
# auth-service/app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.primary_engine = None
        self.read_engine = None
        self.setup_connections()
    
    def setup_connections(self):
        """Setup database connections based on configuration"""
        
        # Primary connection
        self.primary_engine = create_engine(
            settings.db.database_url,
            pool_size=settings.db.pool_size,
            max_overflow=settings.db.max_overflow,
            pool_timeout=settings.db.pool_timeout
        )
        
        # Read replica (if configured)
        if settings.db.read_replica_urls:
            self.read_engine = create_engine(
                settings.db.read_replica_urls[0],  # Use first replica
                pool_size=settings.db.pool_size,
                max_overflow=settings.db.max_overflow
            )
        else:
            self.read_engine = self.primary_engine
        
        logger.info(f"Database connections established for {settings.deployment_type}")
    
    def get_write_session(self):
        """Get session for write operations"""
        SessionLocal = sessionmaker(bind=self.primary_engine)
        return SessionLocal()
    
    def get_read_session(self):
        """Get session for read operations"""
        SessionLocal = sessionmaker(bind=self.read_engine)
        return SessionLocal()

# Global database manager
db_manager = DatabaseManager()
Base = declarative_base()

def get_db():
    """Get database session for general operations"""
    db = db_manager.get_write_session()
    try:
        yield db
    finally:
        db.close()

def get_read_db():
    """Get database session for read-only operations"""
    db = db_manager.get_read_session()
    try:
        yield db
    finally:
        db.close()
```

---

## 🌍 **ENVIRONMENT-SPECIFIC CONFIGURATIONS**

### **1. Development (Current - Single Server):**
```bash
# .env.development
ENVIRONMENT=development
DEPLOYMENT_TYPE=single-server

# Databases on same server
DB__DATABASE_URL=postgresql://admin:Mypassword123@172.16.203.220:25432/auth_db
SHARED__REDIS_URL=redis://172.16.203.220:26379
SHARED__RABBITMQ_URL=amqp://admin:password123@172.16.203.220:5672

DISCOVERY__LOCAL_IP=172.16.203.220
DISCOVERY__PUBLIC_IP=113.161.118.17
```

### **2. Staging (Distributed - Multiple Servers):**
```bash
# .env.staging
ENVIRONMENT=staging
DEPLOYMENT_TYPE=distributed

# Distributed databases
DB__DATABASE_URL=postgresql://auth_user:password@auth-db-server:5432/auth_db
DB__READ_REPLICA_URLS=["postgresql://auth_user:password@auth-db-replica:5432/auth_db"]

SHARED__REDIS_URL=redis://cache-server-1:6379
SHARED__REDIS_CLUSTER_URLS=["redis://cache-server-1:6379", "redis://cache-server-2:6379"]
SHARED__RABBITMQ_URL=amqp://user:pass@queue-server-1:5672
SHARED__RABBITMQ_CLUSTER_URLS=["amqp://user:pass@queue-server-1:5672", "amqp://user:pass@queue-server-2:5672"]

# Service discovery
DISCOVERY__CONTENT_SERVICE_URL=http://content-service:8002
DISCOVERY__ASSIGNMENT_SERVICE_URL=http://assignment-service:8004
DISCOVERY__API_GATEWAY_URL=http://api-gateway:80
```

### **3. Production (Kubernetes/Cloud):**
```bash
# .env.production
ENVIRONMENT=production
DEPLOYMENT_TYPE=kubernetes

# Cloud databases
DB__DATABASE_URL=postgresql://user:pass@auth-db.cluster.amazonaws.com:5432/auth_db
DB__READ_REPLICA_URLS=["postgresql://user:pass@auth-db-ro.cluster.amazonaws.com:5432/auth_db"]

# Managed services
SHARED__REDIS_URL=redis://elasticache.cluster.amazonaws.com:6379
SHARED__RABBITMQ_URL=amqps://user:pass@rabbitmq.cloudamqp.com:5671

# Service mesh
DISCOVERY__CONTENT_SERVICE_URL=http://content-service.microservices.svc.cluster.local:8002
DISCOVERY__ASSIGNMENT_SERVICE_URL=http://assignment-service.microservices.svc.cluster.local:8004
```

---

## 🚀 **MIGRATION STRATEGIES**

### **Strategy 1: Gradual Database Migration**
```yaml
Phase 1: Single Server (Current)
- All services on one server
- Shared PostgreSQL and MongoDB
- Local Redis and RabbitMQ

Phase 2: Database Separation
- Auth DB → Dedicated PostgreSQL server
- Content DB → Dedicated MongoDB server
- Assignment DB → Separate PostgreSQL server
- Shared Redis and RabbitMQ

Phase 3: Service Distribution
- Each service on separate servers
- Load balancers for databases
- Redis cluster
- RabbitMQ cluster

Phase 4: Cloud Migration
- Managed databases (RDS, DocumentDB)
- Managed cache (ElastiCache)
- Managed message queue (SQS/SNS)
- Container orchestration (EKS/AKS)
```

### **Strategy 2: Service Discovery Implementation**
```python
# auth-service/app/core/service_discovery.py
import os
import httpx
from typing import Optional

class ServiceDiscovery:
    def __init__(self):
        self.deployment_type = os.getenv("DEPLOYMENT_TYPE", "single-server")
    
    async def get_service_url(self, service_name: str) -> Optional[str]:
        """Get service URL based on deployment type"""
        
        if self.deployment_type == "single-server":
            # Direct IP access
            service_map = {
                "content-service": f"http://{settings.discovery.local_ip}:8002",
                "assignment-service": f"http://{settings.discovery.local_ip}:8004"
            }
            return service_map.get(service_name)
        
        elif self.deployment_type == "distributed":
            # DNS-based discovery
            return f"http://{service_name}:8000"
        
        elif self.deployment_type == "kubernetes":
            # Kubernetes service discovery
            return f"http://{service_name}.microservices.svc.cluster.local:8000"
        
        return None
    
    async def health_check(self, service_url: str) -> bool:
        """Check if service is healthy"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{service_url}/health", timeout=5.0)
                return response.status_code == 200
        except:
            return False

service_discovery = ServiceDiscovery()
```

---

## 📋 **DEPLOYMENT AUTOMATION**

### **Docker Compose for Different Environments:**

#### **Single Server (development):**
```yaml
# docker-compose.development.yml
version: '3.8'
services:
  auth-service:
    build: ./auth-service
    environment:
      - ENVIRONMENT=development
    ports:
      - "8001:8001"
    depends_on:
      - postgres
      - redis
      - rabbitmq
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_MULTIPLE_DATABASES: auth_db,assignment_db
    ports:
      - "25432:5432"
  
  # ... other services
```

#### **Distributed (staging):**
```yaml
# docker-compose.staging.yml
version: '3.8'
services:
  auth-service:
    build: ./auth-service
    environment:
      - ENVIRONMENT=staging
    ports:
      - "8001:8001"
    external_links:
      - "auth-db-server:auth-db"
      - "cache-server:redis"
```

#### **Kubernetes (production):**
```yaml
# k8s/auth-service-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auth-service
  template:
    spec:
      containers:
      - name: auth-service
        image: auth-service:latest
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DB__DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: auth-db-secret
              key: connection-string
```

---

## 🎯 **BENEFITS OF THIS APPROACH**

### **Zero Code Changes:**
```yaml
✅ Environment variables handle all configurations
✅ Same codebase for all environments
✅ Automatic service discovery
✅ Health checking built-in
✅ Fallback mechanisms ready
```

### **Easy Migration Path:**
```yaml
✅ Single server → Distributed: Update .env only
✅ Distributed → Cloud: Update connection strings
✅ Add read replicas: Update environment variables
✅ Scale services: Container orchestration ready
```

### **Production Ready Features:**
```yaml
✅ Connection pooling configured
✅ Read/write split ready
✅ Cluster support built-in
✅ Health monitoring
✅ Service discovery
✅ Fallback mechanisms
```

---

## 📝 **IMPLEMENTATION STEPS**

### **Immediate (Use current single server):**
1. Implement flexible config system
2. Use environment-based configuration
3. Add service discovery foundation

### **Future Migration (When ready to scale):**
1. Update .env files with new database servers
2. Deploy services to separate servers
3. No code changes required!

**Bạn muốn tôi implement flexible config system này cho Auth Service không?** 🚀
