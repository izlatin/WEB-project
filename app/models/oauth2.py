import time

from sqlalchemy.orm import relation
from authlib.integrations.sqla_oauth2 import (
    OAuth2ClientMixin,
    OAuth2AuthorizationCodeMixin,
    OAuth2TokenMixin,
)
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc7636 import CodeChallenge

from sqlalchemy import orm, Column, Boolean, Text, String, ForeignKey, Integer, DateTime

from app.db_session import SqlAlchemyBase
from app.models import User



class OAuth2Client(SqlAlchemyBase, OAuth2ClientMixin):
    __tablename__ = 'oauth2_client'

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey('User.id', ondelete='CASCADE'))
    # user = relation('User', back_populates='oauth2_client')


class OAuth2AuthorizationCode(SqlAlchemyBase, OAuth2AuthorizationCodeMixin):
    __tablename__ = 'oauth2_code'

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey('User.id', ondelete='CASCADE'))
    # user = relation('User', back_populates='oauth2_code')


class OAuth2Token(SqlAlchemyBase, OAuth2TokenMixin):
    __tablename__ = 'oauth2_token'

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey('User.id', ondelete='CASCADE'))
    user = relation('User', back_populates='oauth2_token')

    def is_refresh_token_active(self):
        if self.revoked:
            return False
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at >= time.time()

        
# class Client(SqlAlchemyBase):
#     """
#     Client (Application)
#     A client is the app which wants to use the resource of a user.
#     It is suggested that the client is registered by a user on your site, but it is not required.
#     """
#     # human readable name, not required
#     name = Column(String(40))

#     # human readable description, not required
#     description = Column(String(400))

#     # creator of the client, not required
#     user_id = Column(ForeignKey('user.id'))
#     # required if you need to support client credential
#     user = orm.relation('User', back_populates='client')

#     client_id = Column(String(40), primary_key=True)
#     client_secret = Column(String(55), unique=True, index=True,
#                               nullable=False)

#     # public or confidential
#     is_confidential = Column(Boolean)

#     _redirect_uris = Column(Text)
#     _default_scopes = Column(Text)

#     @property
#     def client_type(self):
#         if self.is_confidential:
#             return 'confidential'
#         return 'public'

#     @property
#     def redirect_uris(self):
#         if self._redirect_uris:
#             return self._redirect_uris.split()
#         return []

#     @property
#     def default_redirect_uri(self):
#         return self.redirect_uris[0]

#     @property
#     def default_scopes(self):
#         if self._default_scopes:
#             return self._default_scopes.split()
#         return []


# class Grant(SqlAlchemyBase):
#     id = Column(Integer, primary_key=True)

#     user_id = Column(
#         Integer, ForeignKey('user.id', ondelete='CASCADE')
#     )
#     user = orm.relation('User', back_populates='grant')

#     client_id = Column(
#         String(40), ForeignKey('client.client_id'),
#         nullable=False,
#     )
#     client = orm.relation('Client', back_populates='grant')

#     code = Column(String(255), index=True, nullable=False)

#     redirect_uri = Column(String(255))
#     expires = Column(DateTime)

#     _scopes = Column(Text)

#     def delete(self):
#         try:
#             _sess.delete(self)
#         except Exception:
#             _sess.rollback()
#             raise 
#         else:
#             _sess.commit()
            
#         return self

#     @property
#     def scopes(self):
#         if self._scopes:
#             return self._scopes.split()
#         return []

# class Token(SqlAlchemyBase):
#     id = Column(Integer, primary_key=True)
#     client_id = Column(
#         String(40), ForeignKey('client.client_id'),
#         nullable=False,
#     )
#     client = orm.relation('Client', back_populates='token')

#     user_id = Column(
#         Integer, ForeignKey('user.id')
#     )
#     user = orm.relation('User', back_populates='token')

#     # currently only bearer is supported
#     token_type = Column(String(40))

#     access_token = Column(String(255), unique=True)
#     refresh_token = Column(String(255), unique=True)
#     expires = Column(DateTime)
#     _scopes = Column(Text)

#     def delete(self):
#         try:
#             _sess.delete(self)
#         except Exception:
#             _sess.rollback()
#             raise 
#         else:
#             _sess.commit()
#         return self

#     @property
#     def scopes(self):
#         if self._scopes:
#             return self._scopes.split()
#         return []

