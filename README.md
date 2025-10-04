# Eiei Marketplace User Management

## Features

- Register user (email, username, password, phone, role)
- Login (JWT) with enhanced response format
- Logout
- Role management (vendor, organizer)
- Automated CI/CD pipeline with GitHub Actions

## Quick Start

### Run with Docker

```bash
docker-compose up --build
```

### Run locally

```bash
# Install dependencies
make install-dev

# Run the application
make run
```

### Use the docs (like swagger)

```
http://127.0.0.1:8000/docs
```

example for running specific test case

```
python -m pytest -v tests/test_users.py::test_register_user
```

## Development

### Testing

```bash
# Run tests
make test

# Run tests with coverage
make test-cov

# Run tests in Docker
make test-docker
```

### Code Quality

```bash
# Run linting
make lint

# Format code
make format

# Run security checks
make security

# Run all CI checks locally
make ci
```

### Available Make Commands

```bash
make help  # Show all available commands
```

## CI/CD Pipeline

This project uses GitHub Actions for continuous integration. The pipeline includes:

- **Automated Testing**: Runs `python -m pytest -v` on multiple Python versions (3.9, 3.10, 3.11)
- **Code Quality**: Flake8, Black, and isort for code formatting and linting
- **Security**: Safety and Bandit for security vulnerability scanning
- **Coverage**: Code coverage reporting with pytest-cov

The pipeline triggers on:

- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

### Pipeline Jobs

1. **Test**: Runs tests across multiple Python versions
2. **Lint**: Code quality checks (flake8, black, isort)
3. **Security**: Security vulnerability scanning (safety, bandit)

## Repo Structure

```
eieimarketplace-user-management/
|──supabase-dockerfile
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

### Run with Supabase Database

1.

```
docker compose -f docker-compose-supabase.yml up --build
```

2.

```
Back to use postgresLocal :D
```
