from django.contrib.auth.models import User
from django.http import JsonResponse
import jwt

from core.utils import get_token

JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 10000


class AuthenticationMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.META.get('HTTP_AUTHORIZATION'):
            jwt_token = get_token(request.META.get('HTTP_AUTHORIZATION'))
            try:
                payload = jwt.decode(jwt_token, JWT_SECRET,
                                     algorithms=[JWT_ALGORITHM])
            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                return JsonResponse({'message': 'Token is invalid'}, status=400)
            request.user = User.objects.get(id=payload['user_id'])

        return self.get_response(request)

