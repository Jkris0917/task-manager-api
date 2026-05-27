from rest_framework import serializers
from .models import Project, Task
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'email']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length= 8)
    
    class Meta:
        model = User
        fields = ['username','email', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email',''),
            password=validated_data['password']
        )
        return user

class TaskSerializer(serializers.ModelSerializer):
    assignee_detail = UserSerializer(source='assignee', read_only=True)
    
    class Meta:
        model = Task
        fields = ['id','project','title', 'description', 'status', 'priority','assignee','assignee_detail','deadline','created_at', 'updated_at']
        read_only_fields = ['id','project','created_at','updated_at']    

class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id','name','description','owner','task_count','created_at', 'updated_at']
        read_only_fields = ['id','created_at','updated_at', 'owner']
        
    def get_task_count(self,obj):
        return obj.tasks.count()