# Eiei Marketplace User Management

## Features
- Register user (email, username, password, phone, role)
- Login (JWT)
- Logout
- Role management (vendor, organizer)

## Run with Docker
```bash
docker-compose up --build
```

### Use the docs (like swagger)
```
http://127.0.0.1:7001/docs
```

### Unit Testing
```
python -m pytest -v
```

## Repo Structure 
```
eieimarketplace-user-management/
│── app/
│   ├── main.py              # entrypoint ของ FastAPI
│   ├── models.py            # ORM Models (SQLAlchemy)
│   ├── schemas.py           # Pydantic Schemas (request/response validation)
│   ├── database.py          # เชื่อมต่อ DB (SQLAlchemy + session)
│   ├── crud.py              # ฟังก์ชันสำหรับ query DB
│   ├── auth.py              # JWT, password hashing, login/logout
│   └── routers/
│       └── user_router.py   # routes เกี่ยวกับ user (register, login, logout)
│── tests/
│   ├── conftest.py          # ให้ pytest รู้จัก TestClient และใช้ DB memory (sqlite) แทน
│   └── test_users.py        # ทดสอบ register, login, logout
│
│── Dockerfile               # สร้าง image ของ FastAPI app
│── docker-compose.yml       # รวม FastAPI + PostgreSQL
│── requirements.txt         # dependencies
│── README.md                # วิธีรันและอธิบายไฟล์
```
