from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_jwt_identity
)
from flask import current_app

from sqlalchemy.ext.hybrid import hybrid_property

from alicerce.ext.db import db
from alicerce.alicerce_api.models.token_revokedlist import RevokedToken
from alicerce.ext.bcrypt import bcrypt
from alicerce.alicerce_api.util.datetime_util import (
    utc_now,
    get_local_utcoffset,
    make_tzaware,
    localized_dt_string,
)
from alicerce.alicerce_api.util.result import Result


class User(db.Model):
    """Classe responsável por salvar as informações do usuário no banco."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    registered_on = db.Column(db.DateTime, default=utc_now)
    public_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid4()))

    def __repr__(self):
        return (
            f"<Username={self.username}, public_id={self.public_id}, admin={self.admin}>"
        )

    def save_to_db(self):
        """Salva o usuário atual no banco de dados."""
        db.session.add(self)
        db.session.commit()

    def update_password(self, new_password):
        self.password = new_password
        db.session.commit()

    @hybrid_property
    def registered_on_str(self):
        registered_on_utc = make_tzaware(
            self.registered_on, use_tz=timezone.utc, localize=False
        )
        return localized_dt_string(registered_on_utc, use_tz=get_local_utcoffset())

    @property
    def password(self):
        raise AttributeError("password: write-only field")

    @password.setter
    def password(self, password):
        log_rounds = current_app.config.get("BCRYPT_LOG_ROUNDS")
        hash_bytes = bcrypt.generate_password_hash(password, log_rounds)
        self.password_hash = hash_bytes.decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_public_id(cls, public_id):
        return cls.query.filter_by(public_id=public_id).first()
    
    def create_access_refresh_tokens(self):
        now = datetime.now(timezone.utc)
        now = now.timestamp()
        access_token_age = current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES")
        refresh_token_age = current_app.config.get("JWT_REFRESH_TOKEN_EXPIRES")

        payload = dict(
            access_exp = now + access_token_age,
            refresh_exp= now + refresh_token_age,
            iat=now,
            sub=self.public_id,
            admin=self.admin
        )

        access_token = create_access_token(identity=payload)
        refresh_token = create_refresh_token(identity=payload)

        access = RevokedToken(
            access_token,
            "access",
            self.public_id,
            payload["access_exp"]
        )

        access.add()

        refresh = RevokedToken(
            refresh_token,
            "refresh",
            self.public_id,
            payload["refresh_exp"]
        )

        refresh.add()
        
        return [access_token, refresh_token]
    
    def create_access_token(self, refresh_token_age):
        now = datetime.now(timezone.utc)
        now = now.timestamp()
        access_token_age = current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES")
        access_token_age = current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES")

        payload = dict(
            access_exp = now + access_token_age,
            refresh_exp= refresh_token_age,
            iat=now,
            sub=self.public_id,
            admin=self.admin
        )

        access_token = create_access_token(identity = payload)

        access = RevokedToken(
            access_token,
            "access",
            self.public_id,
            payload["access_exp"]
        )

        access.add()

        return access_token

    @staticmethod
    def decode_token(token):

        if token.startswith("Bearer "):
            split = token.split("Bearer")
            token = split[1].strip()

        if RevokedToken.check_if_token_is_revoked(token):
            error = "Token revoked. Please log in again."
            return Result.Fail(error)

        identity = get_jwt_identity()

        user_dict = dict(
            public_id=identity["sub"],
            admin=identity["admin"],
            token=token,
            access_expires_at=identity["access_exp"],
            refresh_expires_at=identity["refresh_exp"],
            expires_at=identity["access_exp"]
        )

        return Result.Ok(user_dict)
