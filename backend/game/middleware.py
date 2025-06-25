from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs

User = get_user_model()

@database_sync_to_async
def get_user_from_session(session_key):
    try:
        session = Session.objects.get(session_key=session_key)
        user_id = session.get_decoded().get('_auth_user_id')
        user = User.objects.get(id=user_id)
        return user
    except (Session.DoesNotExist, User.DoesNotExist, KeyError):
        return AnonymousUser()

class SessionAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Look for sessionid in cookies
        cookies = parse_qs(scope.get('query_string', b'').decode())
        session_key = cookies.get('sessionid', [None])[0]

        if not session_key:
             # Fallback for environments where query string might not be standard
            headers = dict(scope.get('headers', []))
            if b'cookie' in headers:
                cookies = parse_qs(headers[b'cookie'].decode())
                session_key = cookies.get('sessionid', [None])[0]

        scope['user'] = await get_user_from_session(session_key) if session_key else AnonymousUser()
        
        return await super().__call__(scope, receive, send)

def SessionAuthMiddlewareStack(app):
    return SessionAuthMiddleware(app) 