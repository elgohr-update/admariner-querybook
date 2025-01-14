import functools
import flask
from flask_login import current_user
from flask_socketio import disconnect

from app.flask_app import socketio
from lib.event_logger import event_logger
from lib.logger import get_logger

LOG = get_logger(__file__)


def register_socket(url, namespace=None, websocket_logging=True):
    def wrapper(fn):
        @socketio.on(url, namespace=namespace)
        @functools.wraps(fn)
        def handler(*args, **kwargs):
            if not current_user.is_authenticated:
                LOG.error("Unauthorized websocket access")
                disconnect()
            else:
                try:
                    if websocket_logging:
                        event_logger.log_websocket_event(
                            route=namespace + "/" + url,
                            args=args,
                            kwargs=kwargs,
                        )
                    fn(*args, **kwargs)
                except Exception as e:
                    LOG.error(e, exc_info=True)
                    socketio.emit(
                        "error",
                        str(e),
                        namespace=namespace,
                        room=flask.request.sid,
                    )

        handler.__raw__ = fn
        return handler

    return wrapper
