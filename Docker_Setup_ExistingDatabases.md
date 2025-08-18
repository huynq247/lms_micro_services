# 🐳 DOCKER SETUP FOR EXISTING DATABASES

**Scenario**: MongoDB và PostgreSQL đã có sẵn trên máy chủ RedHat
**Cần setup**: Redis, RabbitMQ, Traefik qua Docker
**Kết nối**: Docker containers → Existing databases

---

## 📋 CONTAINERS CẦN THIẾT

### **Containers cần tạo:**
- ✅ Redis (caching)
- ✅ RabbitMQ (messaging)
- ✅ Traefik (API Gateway)
- ✅ Microservices (Auth, Content, Assignment)

### **Databases sử dụng sẵn:**
- 🔗 PostgreSQL (existing) - Auth + Assignment services
- 🔗 MongoDB (existing) - Content service

---

## 🐳 DOCKER-COMPOSE CONFIGURATION

### **docker-compose.yml**

```yaml
version: '3.8'

networks:
  microservices:
    driver: bridge

services:
  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: lms-redis
    ports:
      - "6379:6379"
    networks:
      - microservices
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  # RabbitMQ Message Queue
  rabbitmq:
    image: rabbitmq:3-management-alpine
    container_name: lms-rabbitmq
    ports:
      - "5672:5672"    # AMQP
      - "15672:15672"  # Management UI
    networks:
      - microservices
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: password123
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    restart: unless-stopped

  # Traefik API Gateway
  traefik:
    image: traefik:v3.0
    container_name: lms-gateway
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"    # Dashboard
    networks:
      - microservices
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik.yml:/traefik.yml:ro
      - ./dynamic.yml:/dynamic.yml:ro
    restart: unless-stopped

  # Auth Service
  auth-service:
    build: ./auth-service
    container_name: lms-auth
    ports:
      - "8001:8001"
    networks:
      - microservices
    environment:
      - DATABASE_URL=postgresql://user:password@HOST_IP:5432/auth_db
      - REDIS_URL=redis://redis:6379
      - RABBITMQ_URL=amqp://admin:password123@rabbitmq:5672
    depends_on:
      - redis
      - rabbitmq
    restart: unless-stopped

  # Content Service
  content-service:
    build: ./content-service
    container_name: lms-content
    ports:
      - "8002:8002"
    networks:
      - microservices
    environment:
      - MONGODB_URL=mongodb://user:password@HOST_IP:27017/content_db
      - REDIS_URL=redis://redis:6379
      - RABBITMQ_URL=amqp://admin:password123@rabbitmq:5672
    depends_on:
      - redis
      - rabbitmq
    restart: unless-stopped

  # Assignment Service
  assignment-service:
    build: ./assignment-service
    container_name: lms-assignment
    ports:
      - "8004:8004"
    networks:
      - microservices
    environment:
      - DATABASE_URL=postgresql://user:password@HOST_IP:5432/assignment_db
      - REDIS_URL=redis://redis:6379
      - RABBITMQ_URL=amqp://admin:password123@rabbitmq:5672
    depends_on:
      - redis
      - rabbitmq
    restart: unless-stopped

volumes:
  redis_data:
  rabbitmq_data:
```

---

## 🔧 CONFIGURATION FILES

### **traefik.yml**

```yaml
api:
  dashboard: true
  insecure: true

entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

providers:
  docker:
    exposedByDefault: false
  file:
    filename: /dynamic.yml

certificatesResolvers:
  letsencrypt:
    acme:
      email: your-email@example.com
      storage: acme.json
      httpChallenge:
        entryPoint: web
```

### **dynamic.yml**

```yaml
http:
  routers:
    auth-router:
      rule: "PathPrefix(`/api/auth`)"
      service: "auth-service"
      entryPoints:
        - "web"
    
    content-router:
      rule: "PathPrefix(`/api/content`)"
      service: "content-service"
      entryPoints:
        - "web"
    
    assignment-router:
      rule: "PathPrefix(`/api/assignments`)"
      service: "assignment-service"
      entryPoints:
        - "web"

  services:
    auth-service:
      loadBalancer:
        servers:
          - url: "http://auth-service:8001"
    
    content-service:
      loadBalancer:
        servers:
          - url: "http://content-service:8002"
    
    assignment-service:
      loadBalancer:
        servers:
          - url: "http://assignment-service:8004"
```

---

## 🔗 DATABASE CONNECTION SETUP

### **Environment Variables cần cấu hình:**

```bash
# PostgreSQL (existing server)
DATABASE_URL=postgresql://username:password@SERVER_IP:5432/database_name

# MongoDB (existing server)  
MONGODB_URL=mongodb://username:password@SERVER_IP:27017/database_name

# Redis (Docker container)
REDIS_URL=redis://redis:6379

# RabbitMQ (Docker container)
RABBITMQ_URL=amqp://admin:password123@rabbitmq:5672
```

### **Cần thay thế:**
- `SERVER_IP`: IP của máy chủ RedHat
- `username/password`: Credentials của PostgreSQL/MongoDB
- `database_name`: Tên databases đã tạo

---

## 📋 SETUP COMMANDS

### **1. Tạo project structure:**
```bash
mkdir microservices-lms
cd microservices-lms
mkdir auth-service content-service assignment-service
```

### **2. Tạo configuration files:**
```bash
# Tạo docker-compose.yml, traefik.yml, dynamic.yml
# (copy nội dung từ trên)
```

### **3. Start containers:**
```bash
docker-compose up -d redis rabbitmq traefik
```

### **4. Verify containers:**
```bash
docker-compose ps
docker logs lms-redis
docker logs lms-rabbitmq
```

---

## 🔍 TESTING CONNECTIONS

### **Test Redis:**
```bash
docker exec -it lms-redis redis-cli ping
# Expected: PONG
```

### **Test RabbitMQ:**
- Management UI: http://SERVER_IP:15672
- Login: admin/password123

### **Test Database connections:**
```bash
# PostgreSQL
psql -h SERVER_IP -U username -d database_name

# MongoDB
mongo mongodb://username:password@SERVER_IP:27017/database_name
```

---

## 📝 NEXT STEPS

1. **Setup containers:** Redis, RabbitMQ, Traefik
2. **Create databases:** trên PostgreSQL/MongoDB existing
3. **Build microservices:** theo Week 2-5 checklists
4. **Configure connections:** Update environment variables
5. **Test integration:** Verify all services communicate

**Ready to start với Week 2: Auth Service!** 🚀
