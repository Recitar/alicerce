"""Parsers and serializers for /auth API endpoints."""
from flask_restx import Model
from flask_restx.fields import String, Boolean
from flask_restx.reqparse import RequestParser


auth_reqparser = RequestParser(bundle_errors=True)
passwd_reqparser = RequestParser(bundle_errors=True)
search_reqparser = RequestParser(bundle_errors=True)

auth_reqparser.add_argument(
    name="username", type=str, location="form", required=True, nullable=False
)
auth_reqparser.add_argument(
    name="password", type=str, location="form", required=True, nullable=False
)


passwd_reqparser.add_argument(
    name="current_password", type=str, location="form", required=True, nullable=False
)
passwd_reqparser.add_argument(
    name="new_password", type=str, location="form", required=True, nullable=False
)


search_reqparser.add_argument(
    name="q", type=str, required=True, nullable=False
)

user_model = Model(
    "User",
    {
        "username": String,
        "public_id": String,
        "admin": Boolean,
        "registered_on": String(attribute="registered_on"),
        "access_token_expires_in": String,
        "refresh_token_expires_in": String,
    },
)
