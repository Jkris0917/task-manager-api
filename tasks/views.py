from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Project,Task,ProjectMember
from .serializers import (ProjectSerializer,TaskSerializer,RegisterSerializer)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from .filters import TaskFilter
from .permissions import is_owner, is_member_or_above, is_viewer_or_above
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema

@extend_schema(
    request=RegisterSerializer,
    responses={201: RegisterSerializer},
    description='Register a new user and receive JWT tokens.'
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "message":"User created successfully",
            "username": user.username,
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    responses={200: ProjectSerializer(many=True)},
    description='List all projects the authenticated user is a member of.'
)
@extend_schema(
    methods=['POST'],
    request=ProjectSerializer,
    responses={201: ProjectSerializer},
    description='Create a new project. Creator is auto-assigned as owner.'
)
@api_view(['GET','POST'])
def project_list(request):
    """
    GET: List all projects the authenticated user is a member of.
    POST: Create a new project. The creator is automatically assigned as owner.
    """
    if request.method == 'GET':
        projects = Project.objects.filter(members__user=request.user)
        serializer = ProjectSerializer(projects,many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save(owner=request.user)
            ProjectMember.objects.create(
                user=request.user,
                role='owner',
                project=project
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET','PUT','DELETE'])
def project_detail(request, pk):
    """
    GET: Retrieve project details. Only members can view.
    PUT: Update project details. Only owners can edit.
    DELETE: Delete project. Only owners can delete.
    """
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        if not is_viewer_or_above(request.user,project):
            return Response({'error':"Access Denied"}, status=status.HTTP_403_FORBIDDEN)
        return Response(ProjectSerializer(project).data)
    
    if request.method == 'PUT':
        if not is_owner(request.user,project):
            return Response({"error": "Only owners can edit this project"}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        if not is_owner(request.user, project):
            return Response({"error":"Only owner can delete this project"}, status=status.HTTP_403_FORBIDDEN)
        project.delete()
        return Response({"message":"Project delete", "id": pk})
    
@api_view(['GET', 'POST'])
def task_list(request,project_pk):
    """
    GET: List all tasks in a project. Only members can view.
    POST: Create a new task in the project. Only members can create tasks.
    """
    try:
        project = Project.objects.get(pk=project_pk)
    except Project.DoesNotExist:
        return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        if not is_viewer_or_above(request.user, project):
            return Response({"error":" Access denied"}, status=status.HTTP_403_FORBIDDEN)
        tasks = project.tasks.all()
        filterset = TaskFilter(request.query_params, queryset=tasks)
        ordering = request.query_params.get('ordering', '-created_at')
        allowed_orderings = ['created_at', '-created_at', 'deadline', '-deadline', 'priority', 'title', '-title']
        if ordering in allowed_orderings:
            tasks = filterset.qs.order_by(ordering)
        else:
            tasks = filterset.qs
        return Response(TaskSerializer(tasks, many=True).data)
    
    if request.method == 'POST':
        if not is_member_or_above(request.user, project):
            return Response({"error": "Viewers cannot create tasks"}, status=status.HTTP_403_FORBIDDEN)
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project=project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET','PUT','DELETE'])
def task_detail(request, pk, project_pk):
    """
    GET: Retrieve task details. Only members can view.
    PUT: Update task details. Only members can edit.
    DELETE: Delete task. Only members can delete.
    """
    try:
        project = Project.objects.get(pk=project_pk)
        task = Task.objects.get(pk=pk, project=project)
    except(Project.DoesNotExist, Task.DoesNotExist):
        return Response({"error":"Not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        if not is_viewer_or_above(request.user,project):
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        return Response(TaskSerializer(task).data)
    
    if request.method == 'PUT':
        if not is_member_or_above(request.user,project):
            return Response({"error":"Viewers cannot edit this task"}, status=status.HTTP_403_FORBIDDEN)
        serializer = TaskSerializer(task,data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        if not is_member_or_above(request.user, project):
            return Response({"error": "Viewers cannot delete this task"}, status=status.HTTP_403_FORBIDDEN)
        task.delete()
        return Response({"message":"Task deleted", "id": pk})
    
@api_view(['GET'])
def project_summary(request,project_pk):
    """
    GET: Retrieve project summary including total tasks, tasks by status, overdue tasks, and completion percentage. Only members can view.

    """
    try:
        project = Project.objects.get(pk=project_pk)
    except Project.DoesNotExist:
        return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if not is_viewer_or_above(request.user, project):
        return Response({"error":"Access denied"}, status=status.HTTP_403_FORBIDDEN)
    
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

@api_view(['POST'])
def add_project_member(request,project_pk):
    """
    POST: Add a member to the project. Only owners can add members.
    Request body should include 'username' of the user to add and optional 'role' (default 'viewer').
    
    """
    try:
        project = Project.objects.get(pk=project_pk)
    except Project.DoesNotExist:
        return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if not is_owner(request.user,project):
        return Response({"error": "Only owners can add members"}, status=status.HTTP_403_FORBIDDEN)
    
    username = request.data.get('username')
    role = request.data.get('role', 'viewer')
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    membership, created = ProjectMember.objects.get_or_create(
        user = user,
        project = project,
        defaults={'role':role}
    )
    if not created:
        return Response({"error":"User is already a member"}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        "message": f"{username} added as {role}",
        "username": username,
        "role" : role,
    }, status=status.HTTP_201_CREATED)
    
@api_view(['DELETE'])
def delete_project_member(request,project_pk,user_pk):
    """
    DELETE: Remove a member from the project. Only owners can remove members. Owners cannot remove themselves.
    """
    try:
        project = Project.objects.get(pk=project_pk)
    except Project.DoesNotExist:
        return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if not is_owner(request.user,project):
        return Response({"error": "Only owners can remove members"}, status=status.HTTP_403_FORBIDDEN)
    
    if request.user.pk == user_pk:
        return Response({"error":"Owners cannot remove themselves"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        membership = ProjectMember.objects.get(project=project,user__pk=user_pk)
    except ProjectMember.DoesNotExist:
        return Response({"error": "Member not found"},status=status.HTTP_404_NOT_FOUND)
    
    membership.delete()
    return Response({"message":"Member removed successfully"})
