# 📋 Task Manager API

A production-grade RESTful API for project and task management, built with Django and Django REST Framework. Designed for team-based task tracking with role-based access control, background task processing, and automated testing.

## ✨ Features

- **JWT Authentication** — Secure stateless auth with access/refresh tokens and blacklist-based logout
- **Role-Based Access Control (RBAC)** — Owner, Member, and Viewer roles per project
- **Full CRUD** — Projects and Tasks with nested URL hierarchy
- **Advanced Filtering** — Filter tasks by status, priority, deadline range; sort by any field
- **Project Summary** — Completion percentage and overdue task detection
- **Background Tasks** — Celery + Redis for async overdue task notifications
- **Automated Tests** — 16 tests covering auth, CRUD, filters, and permissions
- **CI/CD** — GitHub Actions runs the full test suite on every push
- **API Documentation** — Auto-generated Swagger UI and ReDoc via drf-spectacular
- **PostgreSQL** backend with Docker support

## 🔗 Live API

**Base URL:** `https://task-manager-api-production-d89b.up.railway.app`

**API Docs:** `https://task-manager-api-production-d89b.up.railway.app/api/docs/`

## 📡 Endpoints

### Auth
| Method | URL | Description | Auth |
|--------|-----|-------------|------|
| POST | `/api/auth/register/` | Register and receive JWT tokens | Public |
| POST | `/api/auth/login/` | Login and receive JWT tokens | Public |
| POST | `/api/auth/logout/` | Blacklist refresh token | Required |
| POST | `/api/auth/refresh/` | Get new access token | Public |

### Projects
| Method | URL | Description | Auth |
|--------|-----|-------------|------|
| GET/POST | `/api/projects/` | List joined projects / create project | Required |
| GET/PUT/DELETE | `/api/projects/<id>/` | Project detail (role-restricted) | Required |
| GET | `/api/projects/<id>/summary/` | Completion % and overdue stats | Required |

### Tasks
| Method | URL | Description | Auth |
|--------|-----|-------------|------|
| GET/POST | `/api/projects/<id>/tasks/` | List / create tasks | Required |
| GET/PUT/DELETE | `/api/projects/<id>/tasks/<id>/` | Task detail (role-restricted) | Required |

### Members
| Method | URL | Description | Auth |
|--------|-----|-------------|------|
| POST | `/api/projects/<id>/members/` | Add member (owner only) | Required |
| DELETE | `/api/projects/<id>/members/<user_id>/` | Remove member (owner only) | Required |

## 🔐 Role-Based Access Control

| Action | Owner | Member | Viewer |
|--------|-------|--------|--------|
| View project & tasks | ✅ | ✅ | ✅ |
| Create / edit tasks | ✅ | ✅ | ❌ |
| Delete tasks | ✅ | ✅ | ❌ |
| Edit project | ✅ | ❌ | ❌ |
| Delete project | ✅ | ❌ | ❌ |
| Manage members | ✅ | ❌ | ❌ |

## 🔍 Filtering & Ordering

```bash
# Filter by status
GET /api/projects/<id>/tasks/?status=todo

# Filter by priority
GET /api/projects/<id>/tasks/?priority=high

# Combined filters
GET /api/projects/<id>/tasks/?status=todo&priority=high

# Filter by deadline range
GET /api/projects/<id>/tasks/?deadline_before=2026-12-31
GET /api/projects/<id>/tasks/?deadline_after=2026-01-01

# Ordering
GET /api/projects/<id>/tasks/?ordering=deadline
GET /api/projects/<id>/tasks/?ordering=-created_at
GET /api/projects/<id>/tasks/?ordering=title
```

## 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.12 | Language |
| Django 6.0 | Web framework |
| Django REST Framework | API layer |
| djangorestframework-simplejwt | JWT authentication |
| django-filter | Advanced filtering |
| Celery + Redis | Background task queue |
| django-celery-beat | Periodic task scheduling |
| drf-spectacular | OpenAPI 3.0 docs + Swagger UI |
| PostgreSQL | Database |
| Docker + Docker Compose | Containerization |
| GitHub Actions | CI/CD |

## ⚙️ Setup (Local)

```bash
git clone https://github.com/Jkris0917/task-manager-api
cd task-manager-api
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

Create a `.env` file:
```env
DB_NAME=task_manager
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost 127.0.0.1
```

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Running Celery (3 terminals)

```bash
# Terminal 1 — Django
python manage.py runserver

# Terminal 2 — Celery worker
celery -A config worker --loglevel=info --pool=solo

# Terminal 3 — Beat scheduler
celery -A config beat --loglevel=info
```

## 🐳 Setup (Docker)

```bash
docker compose up --build
docker compose exec web python manage.py createsuperuser
```

## 🧪 Running Tests

```bash
pytest -v
```

16 tests covering:
- JWT auth flows (register, login, logout, wrong password)
- Project CRUD and ownership isolation
- Task creation, filtering by status/priority, ordering
- Project summary and completion percentage
- RBAC permission boundaries (viewer blocked, member allowed, owner only)

## 📖 API Documentation

Start the server and visit:
- **Swagger UI:** `http://localhost:8000/api/docs/`
- **ReDoc:** `http://localhost:8000/api/redoc/`

## 💡 Example Usage

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "secure123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "secure123"}'

# Create project (use Bearer token)
curl -X POST http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Project"}'

# Add a member
curl -X POST http://localhost:8000/api/projects/1/members/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"username": "jane", "role": "member"}'
```

## 📚 What I Learned

- JWT authentication with access/refresh token rotation and blacklisting
- Role-based access control with per-resource permission checks
- Nested URL routing (projects → tasks hierarchy)
- Background task processing with Celery, Redis, and beat scheduling
- Advanced queryset filtering with django-filter
- Writing automated tests with pytest-django and fixtures
- CI/CD pipeline setup with GitHub Actions
- Auto-generated API documentation with drf-spectacular
- Docker Compose with PostgreSQL healthcheck

---

# 📋 タスク管理API

DjangoとDjango REST Frameworkで構築した本格的なRESTful APIです。
JWT認証、ロールベースアクセス制御、バックグラウンドタスク処理、自動テストを備えたチーム向けタスク管理バックエンドシステムです。

## 主な機能

- **JWT認証** — アクセス・リフレッシュトークンとブラックリストによるログアウト
- **ロールベースアクセス制御（RBAC）** — プロジェクトごとにオーナー・メンバー・ビューワーの役割を設定
- **完全なCRUD操作** — プロジェクトとタスクの作成・取得・更新・削除
- **高度なフィルタリング** — ステータス・優先度・期限でタスクを絞り込み
- **プロジェクト集計** — 完了率と期限超過タスクの自動計算
- **バックグラウンドタスク** — Celery + Redisによる非同期処理
- **自動テスト** — 16件のテストで認証・CRUD・権限を検証
- **CI/CD** — GitHub Actionsでプッシュのたびにテストを自動実行
- **APIドキュメント** — Swagger UIとReDocで自動生成

## セットアップ

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Dockerでの起動

```bash
docker compose up --build
```

## APIドキュメント

```
http://localhost:8000/api/docs/
```