from django.conf import settings
from django.utils import timezone
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import TblUsers


@api_view(['POST'])
@permission_classes([AllowAny])
def google_login_user(request):
    credential = request.data.get('credential')

    if not credential:
        return Response(
            {'error': 'Google credential is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    google_client_id = getattr(settings, 'GOOGLE_CLIENT_ID', None)

    if not google_client_id:
        return Response(
            {'error': 'Google client ID is not configured.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    try:
        idinfo = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            google_client_id
        )
    except ValueError:
        return Response(
            {'error': 'Invalid Google credential.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    email = idinfo.get('email')
    email_verified = idinfo.get('email_verified')

    if not email:
        return Response(
            {'error': 'Google account email not found.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not email_verified:
        return Response(
            {'error': 'Google account email is not verified.'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        user = TblUsers.objects.get(email__iexact=email)
    except TblUsers.DoesNotExist:
        return Response(
            {'error': 'User is not registered in this system.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if not user.is_active:
        return Response(
            {'error': 'User account is inactive.'},
            status=status.HTTP_403_FORBIDDEN
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
    }, status=status.HTTP_200_OK)