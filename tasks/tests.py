import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Project,Task


class TestRegister:
    def test_register_success(self,api_client,db):
        response = api_client.post('/api/auth/register/',{
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'new@example.com'
        }, format='json')
        assert response.status_code == 201
        assert 'token' in response.data
        assert response.data['username'] == 'newuser'
        
    def test_register_duplicate_username(self,api_client,test_user,db):
        response = api_client.post('/api/auth/register/',{
            'username': 'nopassuser'
        },format='json')
        assert response.status_code == 400
    
    def test_register_missing_password(self, api_client, db):
        response = api_client.post('/api/auth/register/', {
            'username': 'nopassuser'
        }, format='json')
        assert response.status_code == 400   
        
    def test_register_short_password(self, api_client,db):
        response = api_client.post('/api/auth/register/',{
            'username': 'shortpass',
            'password': '123'
        },format='json')
        assert response.status_code == 400
        
class TestLogin:
    def test_login_success(self,api_client,test_user,db):
        response = api_client.post('/api/auth/login/',{
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')
        assert response.status_code == 200
        assert 'token' in response.data
        
    def test_login_wrong_password(self, api_client,test_user,db):
        response = api_client.post('/api/auth/login/',{
            'username':'testuser',
            'password': 'wrongpassword'
        }, format = 'json')
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self,api_client, test_user,db):
        response = api_client.post('/api/auth/login/',{
            'username': 'nobody',
            'password': 'nopass123'
        },format='json')
        assert response.status_code == 401

class TestProject:
    def test_create_project(self,auth_client,db):
        client, user = auth_client
        response = client.post('/api/projects/',{
            'name': 'Test project',
            'description': 'A test project'
        }, format='json')
        assert response.status_code == 201
        assert response.data['name'] == 'Test project'
        assert response.data['owner']['username'] == 'testuser'
        
    def test_list_projects(self, auth_client,db):
        client, user = auth_client
        Project.objects.create(name='Project 1', owner=user)
        Project.objects.create(name='Project 2', owner=user)
        response = client.get('/api/projects/')
        assert response.status_code == 200
        assert len(response.data) == 2
        
    def test_unauthorized_cannot_list_projects(self, api_client,db):
        response = api_client.get('/api/projects/')
        assert response.status_code == 401
        
    def test_user_cannot_see_other_users_projects(self, auth_client, db):
        client, user = auth_client
        other_user = User.objects.create_user(
            username='other', password='otherpass123'
        )
        Project.objects.create(name='Other Project', owner=other_user)
        response = client.get('/api/projects/')
        assert response.status_code == 200
        assert len(response.data) == 0
        
    def test_delete_project(self,auth_client,db):
        client, user = auth_client
        project = Project.objects.create(name='To Delete', owner=user)
        response = client.delete(f'/api/projects/{project.id}/')
        assert response.status_code == 200
        assert Project.objects.count() == 0
        
    def test_cannot_delete_other_users_project(self,auth_client,db):
        client,user = auth_client
        other_user = User.objects.create(username='other', password='otherpass123')
        project = Project.objects.create(name='Other Project', owner=other_user)
        response = client.delete(f'/api/projects/{project.id}/')
        assert response.status_code == 404
        
class TestTasks:
    def test_create_task(self, auth_client, db):
        client, user = auth_client
        project = Project.objects.create(name='Test Project', owner=user)
        response = client.post(f'/api/projects/{project.id}/tasks/', {
            'title': 'Test Task',
            'status': 'todo',
            'priority': 'high'
        }, format='json')
        assert response.status_code == 201
        assert response.data['title'] == 'Test Task'
        assert response.data['project'] == project.id

    def test_filter_tasks_by_status(self, auth_client, db):
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

    def test_project_summary(self, auth_client, db):
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

    def test_update_task_status(self, auth_client, db):
        client, user = auth_client
        project = Project.objects.create(name='Test Project', owner=user)
        task = Task.objects.create(
            title='My Task', project=project, status='todo'
        )
        response = client.put(
            f'/api/projects/{project.id}/tasks/{task.id}/',
            {'status': 'done'},
            format='json'
        )
        assert response.status_code == 200
        assert response.data['status'] == 'done'
        
        