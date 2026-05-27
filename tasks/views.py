from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Project,Task
from .serializers import (ProjectSerializer,TaskSerializer,UserSerializer,RegisterSerializer)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = Token.objects.create(user=user)
        return Response({
            "message":"User created successfully",
            "username": user.username,
            "token": token.key
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user is None:
        return Response({'error':"Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "username":user.username})

@api_view(['POST'])
def logout(request):
    try:
        request.user.auth_token.delete()
    except (AttributeError, Token.DoesNotExist):
        pass
    return Response({"message": "Logged out successfully"})

@api_view(['GET','POST'])
def project_list(request):
    if request.method == 'GET':
        projects = Project.objects.filter(owner=request.user)
        serializer = ProjectSerializer(projects,many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET','PUT','DELETE'])
def project_detail(request, pk):
    try:
        project = Project.objects.get(pk=pk, owner=request.user)
    except Project.DoesNotExist:
        return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        return Response(ProjectSerializer(project).data)
    
    if request.method == 'PUT':
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        project.delete()
        return Response({"message":"Project delete", "id": pk})
    
@api_view(['GET', 'POST'])
def task_list(request,project_pk):
    try:
        project = Project.objects.get(pk=project_pk, owner=request.user)
        print(f"DEBUG: Found project {project.id} - {project.name}")
    except Project.DoesNotExist:
        return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        task = project.tasks.all()
        
        status_filter = request.query_params.get('status')
        priority_filter = request.query_params.get('priority')
        if status_filter:
            task = task.filter(status=status_filter)
        if priority_filter:
            task = task.filter(priority=priority_filter)
            
        return Response(TaskSerializer(task, many=True).data)
    
    if request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project=project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET','PUT','DELETE'])
def task_detail(request, pk, project_pk):
    try:
        project = Project.objects.get(pk=project_pk, owner=request.user)
        task = Task.objects.get(pk=pk, project=project)
    except(Project.DoesNotExist, Task.DoesNotExist):
        return Response({"error":"Not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        return Response(TaskSerializer(task).data)
    
    if request.method == 'PUT':
        serializer = TaskSerializer(task,data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        task.delete()
        return Response({"message":"Task deleted", "id": pk})
    
@api_view(['GET'])
def project_summary(request,project_pk):
    try:
        project = Project.objects.get(pk=project_pk, owner=request.user)
    except Project.DoesNotExist:
        return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
    
    tasks = project.tasks.all()
    total = tasks.count()
    by_status = {
        s: tasks.filter(status=s).count() for s in ['todo','in_progress','done']
    }
    overdue = tasks.filter(deadline__lt=__import__('datetime').date.today(), status__in=['todo','in_progress']).count()
    
    return Response({
        "project": project.name,
        "total_tasks": total,
        "by_status": by_status,
        "overdue": overdue,
        "completion": f"{round(by_status['done']/total*100)}%" if total else "0%"
    })
        
