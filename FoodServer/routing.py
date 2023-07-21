from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import orders.routing


application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            orders.routing.websocket_urlpatterns
        )
    ),
})