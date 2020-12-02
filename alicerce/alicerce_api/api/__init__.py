"""API blueprint configuration."""
from flask import Blueprint
from flask_restx import Api, Resource


from alicerce.alicerce_api.api.auth.endpoints import auth_ns, search_ns


api_bp = Blueprint("api", __name__, url_prefix="/api/v1")
authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}


api = Api(
    app=api_bp,
    version="0.0.1",
    title="Alicerce API",
    description="Welcome to the Swagger UI documentation for the Alicerce API.",
    authorizations=authorizations,
    doc="/docs",
)


api.add_namespace(auth_ns, path="/auth")
api.add_namespace(search_ns, path="/search")


