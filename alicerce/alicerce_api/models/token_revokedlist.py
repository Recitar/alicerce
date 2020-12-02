"""Class definition for BlacklistedToken."""
from sqlalchemy.orm.exc import NoResultFound
from datetime import timezone, datetime

from alicerce.ext.db import db
from alicerce.alicerce_api.util.datetime_util import utc_now, dtaware_fromtimestamp


class RevokedToken(db.Model):
    """RevokedToken Model para armazenar JWT tokens."""

    __tablename__ = "token_revokedlist"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    token_type = db.Column(db.String(10), nullable=False)
    user_identity = db.Column(db.String(50), nullable=False)
    revoked = db.Column(db.Boolean, nullable=False, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, token, token_type, user_identity, expires_at):
        self.token = token
        self.token_type = token_type
        self.user_identity = user_identity
        self.expires_at = dtaware_fromtimestamp(expires_at, use_tz=timezone.utc)

    def __repr__(self):
        return (
            f"<Token={self.token}, type={self.token_type}, revoked={self.revoked}>"
        )

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def revoke_token(cls, token, user_public_id):
        try:
            token = cls.query.filter_by(
                token=token, user_identity=user_public_id
            ).first()
            token.revoked = True
            db.session.commit()
        except NoResultFound:
            print("Could not find the token {}".format(token))

    @classmethod
    def check_if_token_is_revoked(cls, token):
        try:
            token = cls.query.filter_by(token=token).first()
            return token.revoked
        except NoResultFound:
            return True

    @classmethod
    def prune_database(cls):
        """Remove os tokens que expiraram do banco."""
        now = datetime.now(tz=timezone.utc)
        expired = cls.query.filter(cls.expires_at < now).all()
        for token in expired:
            db.session.delete(token)
        db.session.commit()
