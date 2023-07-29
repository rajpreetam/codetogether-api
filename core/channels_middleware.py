import jwt
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser, User
from django.conf import settings


class JWTAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        try:
            token = self.extract_token(scope)
            if token:
                decoded_payload = await self.decode_token(token)
                user = await self.get_user(decoded_payload)

                # Add the authenticated user to the scope
                scope['user'] = user
            else:
                # If no token or invalid token, use AnonymousUser
                scope['user'] = AnonymousUser()
        except Exception as e:
            print(f"Error during authentication: {e}")
            # Handle any authentication errors here

        return await super().__call__(scope, receive, send)

    def extract_token(self, scope):
        auth_headers = dict(scope.get('headers', {}))
        authorization = auth_headers.get(b'authorization', b'').decode('utf-8')
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == 'bearer':
            return parts[1]
        return None

    @database_sync_to_async
    def decode_token(self, token):
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @database_sync_to_async
    def get_user(self, decoded_payload):
        try:
            user_id = decoded_payload['user_id']
            user = User.objects.get(id=user_id)
            return user
        except User.DoesNotExist:
            return AnonymousUser()  # Return an AnonymousUser if no user found or JWT is invalid
