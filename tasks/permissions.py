from .models import ProjectMember

def get_user_role(user, project):
    try:
        membership = ProjectMember.objects.get(user=user, project=project)
        return membership.role
    except ProjectMember.DoesNotExist:
        return None

def is_owner(user, project):
    return get_user_role(user, project) == 'owner'

def is_member_or_above(user, project):
    return get_user_role(user, project) in ['owner', 'member']

def is_viewer_or_above(user, project):
    return get_user_role(user, project) in ['owner', 'member', 'viewer']