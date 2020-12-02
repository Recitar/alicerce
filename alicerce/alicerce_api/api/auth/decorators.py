"""Decorators that decode and verify authorization tokens."""
from functools import wraps

from flask import request

from alicerce.alicerce_api.api.exceptions import ApiUnauthorized, ApiForbidden
from alicerce.alicerce_api.models.user import User

from flask_jwt_extended import(
    verify_jwt_refresh_token_in_request,
    verify_jwt_in_request,
)


def token_required(f):
    """Allow access to the wrapped function if the request contains a valid access token."""

    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        token_payload = _check_token(admin_only=False)
        for name, val in token_payload.items():
            setattr(decorated, name, val)
        return f(*args, **kwargs)

    return decorated


def refresh_token_required(f):
    """Allow access to the wrapped function if the request contains a valid refresh token."""

    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_refresh_token_in_request()
        token_payload = _check_token(admin_only=False)
        for name, val in token_payload.items():
            setattr(decorated, name, val)
        return f(*args, **kwargs)

    return decorated


def admin_token_required(f):
    """Execute function if request contains valid access token AND user is admin."""

    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        token_payload = _check_token(admin_only=True)
        if not token_payload["admin"]:
            raise ApiForbidden()
        for name, val in token_payload.items():
            setattr(decorated, name, val)
        return f(*args, **kwargs)

    return decorated


def _check_token(admin_only):
    token = request.headers.get("Authorization")
    if not token:
        raise ApiUnauthorized(description="Unauthorized", admin_only=admin_only)
    result = User.decode_token(token)
    if result.failure:
        raise ApiUnauthorized(
            description=result.error,
            admin_only=admin_only,
            error="invalid_token",
            error_description=result.error,
        )
    return result.value
