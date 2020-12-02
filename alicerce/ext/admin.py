from flask import flash
from flask_admin import Admin
from flask_admin.actions import action
from flask_admin.menu import MenuLink
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import AdminIndexView
from flask_simplelogin import login_required

from alicerce.ext.db import db
from alicerce.alicerce_api.models.user import User
from alicerce.alicerce_api.models.token_revokedlist import RevokedToken

AdminIndexView._handle_view = login_required(AdminIndexView._handle_view)
ModelView._handle_view = login_required(ModelView._handle_view)

admin = Admin()


class UserAdmin(ModelView):
    """Interface admin de user"""

    column_list = ["admin", "username", "registered_on", "public_id"]

    column_labels = {"username": "User login", "password_hash": "Password"}

    column_searchable_list = ["username"]

    form_columns = ["username", "password_hash", "admin"]

    form_edit_rules = ['username', 'admin']

    def on_model_change(self, form, User, is_created=False):   
        if is_created:
            User.password = form.password_hash.data


class TokensAdmin(ModelView):

    can_create = False
    can_edit = False

    @action("delete_expired", "Delete expired tokens", "Are you sure?")
    def delete_expired_tokens(self, ids):
        RevokedToken.prune_database()
        flash("Expired tokens removed successfully!", "success")

 

def init_app(app):
    admin.name = app.config.get("ADMIN_NAME", "SucupiraBot")
    admin.template_mode = app.config.get("ADMIN_TEMPLATE_MODE", "bootstrap3")
    admin.init_app(app)


    admin.add_views(
        UserAdmin(User, db.session),
        TokensAdmin(RevokedToken, db.session)
    )


    admin.add_link(
        MenuLink(
            name="Chatbot",
            url="/#chatbot"        )
    )

    admin.add_link(
        MenuLink(
            name="API",
            url="/api/v1/docs"        )
    )
    

    admin.add_link(
        MenuLink(
            name="Logout",
            url=app.config.get("SIMPLELOGIN_LOGOUT_URL"),
            icon_type="glyph",
            icon_value="glyphicon-log-out"
        )
    )