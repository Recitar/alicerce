"""Business logic for /auth API endpoints."""
from http import HTTPStatus

from flask import current_app, jsonify
from flask_restx import abort

from alicerce.alicerce_api.models.user import User
from alicerce.alicerce_api.models.token_revokedlist import RevokedToken
from alicerce.alicerce_api.api.auth.decorators import (
    token_required, refresh_token_required
)
from alicerce.alicerce_api.util.datetime_util import (
    remaining_fromtimestamp, format_timespan_digits,
)
from alicerce.bot.qa import get_answer

def process_login_request(username, password):
    user = User.find_by_username(username)
    if not user:
        abort(HTTPStatus.UNAUTHORIZED, f"User '{username}' doesn't exist", status="fail")
    elif not user.check_password(password):
        abort(HTTPStatus.UNAUTHORIZED, "Wrong credentials", status="fail")
    
    access_token, refresh_token = user.create_access_refresh_tokens()
    return _create_auth_successful_response(
        access_token,
        refresh_token,
        status_code=HTTPStatus.OK,
        message="successfully logged in",
    )


@token_required
def process_update_password_request(current_password, new_password):
    public_id = process_update_password_request.public_id
    user = User.find_by_public_id(public_id)
    if not user.check_password(current_password):
        abort(HTTPStatus.UNAUTHORIZED, "Wrong credentials", status="fail")
    user.update_password(new_password)
    response = jsonify(
        status="success",
        message="Password was successfully updated.",
    )
    response.status_code = HTTPStatus.OK
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return response


@token_required
def get_logged_in_user():
    public_id = get_logged_in_user.public_id
    user = User.find_by_public_id(public_id)
    access_expires_at = get_logged_in_user.access_expires_at
    refresh_expires_at = get_logged_in_user.refresh_expires_at
    user.access_token_expires_in = format_timespan_digits(
        remaining_fromtimestamp(access_expires_at)
    )
    user.refresh_token_expires_in = format_timespan_digits(
        remaining_fromtimestamp(refresh_expires_at)
    )
    return user


@token_required
def process_logout_access_request():
    token = process_logout_access_request.token
    public_id = process_logout_access_request.public_id
    RevokedToken.revoke_token(token, public_id)
    response_dict = dict(status="success", message="successfully logged out")
    return response_dict, HTTPStatus.OK


@refresh_token_required
def process_logout_refresh_request():
    token = process_logout_refresh_request.token
    public_id = process_logout_refresh_request.public_id
    RevokedToken.revoke_token(token, public_id)
    response_dict = dict(status="success", message="successfully logged out")
    return response_dict, HTTPStatus.OK


@refresh_token_required
def process_refresh_request():
    expires_at = process_refresh_request.expires_at
    public_id = process_refresh_request.public_id
    user = User.find_by_public_id(public_id)
    token = process_refresh_request.token
    return _create_auth_successful_response(
        access_token=user.create_access_token(expires_at),
        refresh_token=token,
        status_code=HTTPStatus.CREATED,
        message="Access token successfully created.",
    )


@token_required
def process_search_request(query):
    answer = get_answer(query)
    response =  jsonify(
        status="success",
        message="Successful search",
        answer=answer
    )
    response.status_code = HTTPStatus.OK
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return response


def _create_auth_successful_response(access_token, refresh_token, status_code, message):
    response = jsonify(
        status="success",
        message=message,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        access_expires_in=_get_token_expire_time("access_token"),
        refresh_expires_in=_get_token_expire_time("refresh_token"),
    )
    response.status_code = status_code
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return response
    

def _get_token_expire_time(token_name):
    expires_in_seconds = current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES")
    if token_name == "refresh_token":
        expires_in_seconds = current_app.config.get("JWT_REFRESH_TOKEN_EXPIRES")
    return expires_in_seconds if not current_app.config["TESTING"] else 5