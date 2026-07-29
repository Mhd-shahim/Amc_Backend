from django.contrib.auth.hashers import check_password
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .authentications import TblUsersJWTAuthentication
from .permissions import IsSuperAdmin, IsAuthenticatedTblUser
from .serializers import UserCreateSerializer
from rest_framework.decorators import api_view, authentication_classes,permission_classes

from .models import TblUsers


@api_view(['POST'])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {'error': 'Email and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = TblUsers.objects.get(email=email)
    except TblUsers.DoesNotExist:
        return Response(
            {'error': 'Invalid email or password.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {'error': 'User account is inactive.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if not check_password(password, user.password_hash):
        return Response(
            {'error': 'Invalid email or password.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])

    refresh = RefreshToken()
    refresh['user_id'] = user.id_user
    refresh['email'] = user.email
    refresh['role'] = user.role

    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': {
            'id_user': user.id_user,
            'full_name': user.full_name,
            'email': user.email,
            'phone': user.phone,
            'role': user.role,
            'is_active': user.is_active,
        }
    })

#---------3.Users APIs----------------

# 1. Create User (Only accessible by Super Admin)
@api_view(['POST'])
@authentication_classes([TblUsersJWTAuthentication])
@permission_classes([IsSuperAdmin])
def create_user(request):
    serializer = UserCreateSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {
                'id_user': user.id_user,
                'full_name': user.full_name,
                'email': user.email,
                'phone': user.phone,
                'role': user.role,
                'is_active': user.is_active,
                'created_at': user.created_at,
            },
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#2. List Users 
@api_view(['GET'])
@authentication_classes([TblUsersJWTAuthentication])
@permission_classes([IsAuthenticatedTblUser])
def list_users(request):
    users = TblUsers.objects.all()
    serializer = UserCreateSerializer(users, many=True)
    return Response(serializer.data)

#3. Edit User (Only accessible by Super Admin)
@api_view(['PUT'])
@authentication_classes([TblUsersJWTAuthentication])
@permission_classes([IsSuperAdmin])
def edit_user(request, user_id):
    try:
        user = TblUsers.objects.get(pk=user_id)
    except TblUsers.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserCreateSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 4. Delete User (Only accessible by Super Admin)
@api_view(['DELETE'])
@authentication_classes([TblUsersJWTAuthentication])
@permission_classes([IsSuperAdmin])
def delete_user(request, user_id):
    try:
        user = TblUsers.objects.get(pk=user_id)
        user.delete()
        return Response({'message': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    except TblUsers.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)