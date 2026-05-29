import pytest
from django.contrib.auth.models import User
from .models import Project,Task

@pytest.mark.django_db
def test_register_returns_token(api_client):
    response = api_client.post('/api/auth/register/',{
        'username':'newuser',
        'password':'newpass123',
        'email': 'new@example.com'
    })
    assert response.status_code == 201
    assert 'access' in response.data
    assert 'refresh' in response.data
    
@pytest.mark.django_db
def test_login_returns_token(api_client,create_user):
    create_user()
    response = api_client.post('/api/auth/login/',{
        'username' : 'testuser',
        'password' : 'testpass123',
    })
    assert response.status_code == 200
    assert 'access' in response.data
    
@pytest.mark.django_db
def test_logout_blacklists_token(api_client, create_user):
    create_user()
    login_response = api_client.post('/api/auth/login/', {
        'username': 'testuser',
        'password': 'testpass123'
    })
    access_token = login_response.data['access']
    refresh_token = login_response.data['refresh']

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    api_client.post('/api/auth/logout/', {'refresh': refresh_token})

    refresh_response = api_client.post('/api/auth/refresh/', {'refresh': refresh_token})
    assert refresh_response.status_code == 401

@pytest.mark.django_db
def test_login_wrong_password(api_client, create_user):
    create_user()
    response = api_client.post('/api/auth/login/',{
        'username':'testuser',
        'password':'wrongpassword'
    })
    assert response.status_code == 401

# ─── Project Tests ─────────────────────────────────────

@pytest.mark.django_db
def test_create_project(auth_client):
    client, user = auth_client
    response = client.post('/api/projects/',{
        'name': 'Test Project',
        'description': 'A test project'
    }, format='json')
    assert response.status_code == 201

@pytest.mark.django_db
def test_list_projects_only_own(auth_client):
    client, user = auth_client
    other_user = User.objects.create_user(
        username='other', password='otherpass123'
    )
    Project.objects.create(name='Other Project', owner=other_user)
    response = client.get('/api/projects/')
    assert response.status_code == 200
    assert len(response.data) == 0

@pytest.mark.django_db
def test_delete_project(auth_client):
    client, user = auth_client
    project = Project.objects.create(name='To Delete', owner=user)
    response = client.delete(f'/api/projects/{project.id}/')
    assert response.status_code == 200
    assert Project.objects.count() == 0

# ─── Task Tests ────────────────────────────────────────

@pytest.mark.django_db
def test_create_task(auth_client):
    client, user = auth_client
    project = Project.objects.create(name='Test Project', owner=user)
    response = client.post(f'/api/projects/{project.id}/tasks/', {
        'title': 'Test Task',
        'status': 'todo',
        'priority': 'high'
    }, format='json')
    assert response.status_code == 201
    assert response.data['title'] == 'Test Task'
    assert Task.objects.filter(project=project, title='Test Task').exists()

@pytest.mark.django_db
def test_filter_tasks_by_status(auth_client):
    client, user = auth_client
    project = Project.objects.create(name='Test Project', owner=user)
    Task.objects.create(title='Todo Task',    project=project, status='todo')
    Task.objects.create(title='Done Task',    project=project, status='done')
    Task.objects.create(title='Another Done', project=project, status='done')
    response = client.get(
        f'/api/projects/{project.id}/tasks/?status=done'
    )
    assert response.status_code == 200
    assert len(response.data) == 2

# ─── Summary Tests ─────────────────────────────────────

@pytest.mark.django_db
def test_project_summary(auth_client):
    client, user = auth_client
    project = Project.objects.create(name='Test Project', owner=user)
    Task.objects.create(title='T1', project=project, status='todo')
    Task.objects.create(title='T2', project=project, status='done')
    Task.objects.create(title='T3', project=project, status='done')
    response = client.get(f'/api/projects/{project.id}/summary/')
    assert response.status_code == 200
    assert response.data['total_tasks'] == 3
    assert response.data['by_status']['done'] == 2
    assert response.data['completion'] == '67%'
    
# ─── Filter Test ─────────────────────────────────────────

@pytest.mark.django_db
def test_filter_task_by_priority(auth_client):
    client, user = auth_client
    project = Project.objects.create(name='Test Project', owner=user)
    Task.objects.create(title='T1', project=project, priority='high')
    Task.objects.create(title='T2', project=project, priority='high')
    Task.objects.create(title='T3', project=project, priority='low')
    response = client.get(f'/api/projects/{project.id}/tasks/?priority=high')
    assert len(response.data) == 2
    
@pytest.mark.django_db
def test_filter_task_combined(auth_client):
    client, user = auth_client
    project = Project.objects.create(name='Test Project', owner=user)
    Task.objects.create(title='T1', project=project,status='todo', priority='high')
    Task.objects.create(title='T2', project=project,status='todo', priority='low')
    Task.objects.create(title='T3', project=project,status='done', priority='high')
    Task.objects.create(title='T4', project=project,status='done', priority='low')
    response = client.get(f'/api/projects/{project.id}/tasks/?status=todo&priority=high')
    assert len(response.data) == 1
    
@pytest.mark.django_db
def test_task_ordering(auth_client):
    client, user = auth_client
    project = Project.objects.create(name='Test Project', owner=user)
    Task.objects.create(title='A Task', project=project)
    Task.objects.create(title='B Task', project=project)
    response = client.get(f'/api/projects/{project.id}/tasks/?ordering=title')
    assert response.data[0]['title'] == 'A Task'
