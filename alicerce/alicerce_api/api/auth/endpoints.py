"""API endpoint definitions for /auth namespace."""
from http import HTTPStatus

from flask_restx import Namespace, Resource

from alicerce.alicerce_api.api.auth.dto import (
    auth_reqparser, user_model, passwd_reqparser, search_reqparser
)
from alicerce.alicerce_api.api.auth.business import (
    process_login_request,
    get_logged_in_user,
    process_update_password_request,
    process_logout_access_request,
    process_logout_refresh_request,
    process_refresh_request,
    process_search_request
)
from alicerce.ext.limiter import limiter


auth_ns = Namespace(name="auth", validate=True)
auth_ns.models[user_model.name] = user_model

search_ns = Namespace(name="sucupira", validate=True)


@auth_ns.route("/login", endpoint="auth_login")

class LoginUser(Resource):
    """Handles HTTP requests to URL: /api/v1/auth/login."""

    # decorators = [limiter.limit('6 per day')]
    @auth_ns.expect(auth_reqparser)
    @auth_ns.response(int(HTTPStatus.OK), "Login succeeded.")
    @auth_ns.response(int(HTTPStatus.UNAUTHORIZED), "Username or password does not match")
    @auth_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @auth_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def post(self):
        """Autentica um usuário existente e retorna o token de acesso e o token de atualização."""
        request_data = auth_reqparser.parse_args()
        username = request_data.get("username")
        password = request_data.get("password")
        return process_login_request(username, password)


@auth_ns.route("/user", endpoint="auth_user")
class GetUser(Resource):
    """Handles HTTP requests to URL: /api/v1/auth/user."""

    @auth_ns.doc(security="Bearer")
    @auth_ns.response(int(HTTPStatus.OK), "Token is currently valid.", user_model)
    @auth_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @auth_ns.response(int(HTTPStatus.UNAUTHORIZED), "Token is invalid or expired.")
    @auth_ns.marshal_with(user_model)
    def get(self):
        """Verifica o token de acesso e retorna as informações do usuário."""
        return get_logged_in_user()

    @auth_ns.doc(security="Bearer")
    @auth_ns.response(int(HTTPStatus.OK), "Password was successfully updated.")
    @auth_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @auth_ns.response(int(HTTPStatus.UNAUTHORIZED), "Token is invalid or expired or password is incorrect.")
    @auth_ns.expect(passwd_reqparser)
    def put(self):
        """Permite substituir a senha antiga por uma nova senha."""
        request_data = passwd_reqparser.parse_args()
        current_password = request_data.get("current_password")
        new_password = request_data.get("new_password")
        return process_update_password_request(current_password, new_password)


@auth_ns.route("/logout/access", endpoint="auth_logout_access")
class LogoutAccess(Resource):
    """Handles HTTP requests to URL: /logout/access."""

    @auth_ns.doc(security="Bearer")
    @auth_ns.response(int(HTTPStatus.OK), "Log out succeeded, token is no longer valid.")
    @auth_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @auth_ns.response(int(HTTPStatus.UNAUTHORIZED), "Token is invalid or expired.")
    @auth_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def post(self):
        """Revoga o token de acesso, invalidando o uso dele."""
        return process_logout_access_request()


@auth_ns.route("/logout/refresh", endpoint="auth_logout_refresh")
class LogoutRefresh(Resource):
    """Handles HTTP requests to URL: /logout/refresh."""

    @auth_ns.doc(security="Bearer")
    @auth_ns.response(int(HTTPStatus.OK), "Log out succeeded, token is no longer valid.")
    @auth_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @auth_ns.response(int(HTTPStatus.UNAUTHORIZED), "Token is invalid or expired.")
    @auth_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def post(self):
        """Revoga o token de atualização, invalidando o uso dele."""
        return process_logout_refresh_request()


@auth_ns.route("/refresh", endpoint="auth_refresh")
class TokenRefresh(Resource):
    
    @auth_ns.doc(security="Bearer")
    @auth_ns.response(int(HTTPStatus.CREATED), "Access token was successfully created.")
    @auth_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @auth_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def post(self):
        """Permite a criação de um novo token de acesso."""
        return process_refresh_request()


@search_ns.route("/qa", endpoint="qa_search")
class QASearch(Resource):
    @search_ns.doc(security="Bearer")
    @search_ns.expect(search_reqparser)
    def get(self):
        """Permite a consulta à base através de uma pergunta."""
        request_data = search_reqparser.parse_args()
        query = request_data.get("q")
        return process_search_request(query)
