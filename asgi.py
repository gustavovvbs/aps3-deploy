from hypercorn.middleware import AsyncioWSGIMiddleware
from app import create_app

app = create_app()
asgi_app = AsyncioWSGIMiddleware(app)