import pytest
from django.contrib.auth.models import User
from .models import Project,Task,ProjectMember


def create_project_with_membership(user, name='Test Project'):
    project = Project.objects.create(name=name, owner=user)
    ProjectMember.objects.create(user=user,project=project,role='owner')
    return project

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
    project = create_project_with_membership(user, name='To Delete')
    response = client.delete(f'/api/projects/{project.id}/')
    assert response.status_code == 200
    assert Project.objects.count() == 0

# ─── Task Tests ────────────────────────────────────────

@pytest.mark.django_db
def test_create_task(auth_client):
    client, user = auth_client
    project = create_project_with_membership(user, name='Test Project')
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
    project = create_project_with_membership(user, name='Test Project')
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
    project = create_project_with_membership(user, name='Test Project')
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
    project = create_project_with_membership(user, name='Test Project')
    Task.objects.create(title='T1', project=project, priority='high')
    Task.objects.create(title='T2', project=project, priority='high')
    Task.objects.create(title='T3', project=project, priority='low')
    response = client.get(f'/api/projects/{project.id}/tasks/?priority=high')
    assert len(response.data) == 2
    
@pytest.mark.django_db
def test_filter_task_combined(auth_client):
    client, user = auth_client
    project = create_project_with_membership(user, name='Test Project')
    Task.objects.create(title='T1', project=project,status='todo', priority='high')
    Task.objects.create(title='T2', project=project,status='todo', priority='low')
    Task.objects.create(title='T3', project=project,status='done', priority='high')
    Task.objects.create(title='T4', project=project,status='done', priority='low')
    response = client.get(f'/api/projects/{project.id}/tasks/?status=todo&priority=high')
    assert len(response.data) == 1
    
@pytest.mark.django_db
def test_task_ordering(auth_client):
    client, user = auth_client
    project = create_project_with_membership(user, name='Test Project')
    Task.objects.create(title='A Task', project=project)
    Task.objects.create(title='B Task', project=project)
    response = client.get(f'/api/projects/{project.id}/tasks/?ordering=title')
    assert response.data[0]['title'] == 'A Task'

@pytest.mark.django_db
def test_viewer_cannot_create_task(api_client,create_user,auth_client):
    client, owner = auth_client
    project = create_project_with_membership(owner)
    
    viewer = create_user(username='viewer',password='viewpass123')
    ProjectMember.objects.create(user=viewer,project=project,role='viewer')
    
    viewer_response = api_client.post('/api/auth/login/',{
        'username':'viewer', 'password':'viewpass123'
    })
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {viewer_response.data['access']}')

    response = api_client.post(f"/api/projects/{project.id}/tasks/",{
        'title': 'Should Fail','status':'todo'
    },format='json')
    
    assert response.status_code == 403
    
@pytest.mark.django_db
def test_non_owner_cannot_delete_project(api_client,create_user,auth_client):
    client,owner = auth_client
    project = create_project_with_membership(owner)
    
    member = create_user(username='member',password='memberpass123')
    ProjectMember.objects.create(user=member,project=project, role='member')
    
    member_response = api_client.post('/api/auth/login/',{
        'username':'member','password':'memberpass123'
    })
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {member_response.data['access']}')
    
    response = api_client.delete(f"/api/projects/{project.id}/")
    assert response.status_code == 403
    
@pytest.mark.django_db
def test_owner_can_add_member(auth_client,create_user):
    client, owner = auth_client
    project = create_project_with_membership(owner)
    new_user = create_user(username='newmember', password='pass123')
    
    response= client.post(f"/api/projects/{project.id}/members/",{
        'username':'newmember',
        'role': 'member'
    },format='json')
    assert response.status_code == 201
    assert ProjectMember.objects.filter(user=new_user,project=project).exists()