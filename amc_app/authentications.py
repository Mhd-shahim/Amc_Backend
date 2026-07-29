from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import TblUsers


class TblUsersJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        jwt_auth = JWTAuthentication()
        header = jwt_auth.get_header(request)

        if header is None:
            return None

        raw_token = jwt_auth.get_raw_token(header)

        if raw_token is None:
            return None

        validated_token = jwt_auth.get_validated_token(raw_token)
        user_id = validated_token.get('user_id')

        if not user_id:
            raise AuthenticationFailed('Invalid token.')

        try:
            user = TblUsers.objects.get(id_user=user_id)
        except TblUsers.DoesNotExist:
            raise AuthenticationFailed('User not found.')

        if not user.is_active:
            raise AuthenticationFailed('User account is inactive.')

        return user, validated_token