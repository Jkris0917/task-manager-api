# 📋 Task Manager API

A RESTful API for project and task management, built with Django and 
Django REST Framework. Designed for team-based task tracking with 
per-user project isolation and real-time progress reporting.

## Features

- User registration and token-based authentication
- Full CRUD for Projects and Tasks
- Tasks nested under Projects (realistic data hierarchy)
- Filter tasks by status and priority
- Project summary with completion percentage and overdue detection
- PostgreSQL backend with Docker support

## Endpoints

| Method | URL | Description | Auth |
|--------|-----|-------------|------|
| POST | `/api/auth/register/` | Create account | Public |
| POST | `/api/auth/login/` | Get token | Public |
| POST | `/api/auth/logout/` | Invalidate token | Required |
| GET/POST | `/api/projects/` | List / create projects | Required |
| GET/PUT/DELETE | `/api/projects/<id>/` | Project detail | Required |
| GET/POST | `/api/projects/<id>/tasks/` | List / create tasks | Required |
| GET/PUT/DELETE | `/api/projects/<id>/tasks/<id>/` | Task detail | Required |
| GET | `/api/projects/<id>/summary/` | Project stats | Required |

## Tech Stack

- Python 3.12
- Django 6.0
- Django REST Framework
- PostgreSQL
- Docker + Docker Compose
- python-dotenv

## Setup (Local)

```bash
git clone https://github.com/Jkris0917/task-manager-api
cd task-manager-api
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Create .env:
# DB_NAME=task_manager
# DB_USER=postgres
# DB_PASSWORD=yourpassword
# DB_HOST=localhost
# DB_PORT=5432

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Setup (Docker)

```bash
docker compose up --build
docker compose exec web python manage.py createsuperuser
```

## Example Usage

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "secure123"}'

# Create project
curl -X POST http://localhost:8000/api/projects/ \
  -H "Authorization: Token <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Project"}'
```

## What I Learned

- Nested URL routing (projects → tasks hierarchy)
- ForeignKey relationships with related_name
- Nested serializers for related objects
- SerializerMethodField for computed fields
- Owner-based queryset filtering for data isolation
- Docker Compose with PostgreSQL healthcheck

---

# 📋 タスク管理API

DjangoとDjango REST Frameworkで構築したRESTful APIです。
プロジェクトとタスクをチームで管理するためのバックエンドシステムです。

## 主な機能

- ユーザー登録とトークン認証
- プロジェクトとタスクの完全なCRUD操作
- タスクはプロジェクト配下に階層管理
- ステータス・優先度によるタスクフィルタリング
- 完了率と期限超過タスクの自動集計
- PostgreSQLとDockerに対応

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