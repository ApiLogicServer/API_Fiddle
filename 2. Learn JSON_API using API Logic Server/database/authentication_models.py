# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask import abort
from safrs import jsonapi_rpc
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import create_access_token


########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
# Alter this file per your database maintenance policy
#    See https://apilogicserver.github.io/Docs/Project-Rebuild/#rebuilding
#
# mypy: ignore-errors

from safrs import SAFRSBase
from flask_login import UserMixin
import safrs, flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy() 
Baseauthentication = declarative_base()  # type: flask_sqlalchemy.model.DefaultMeta
metadata = Baseauthentication.metadata

#NullType = db.String  # datatype fixup
#TIMESTAMP= db.TIMESTAMP

from sqlalchemy.dialects.sqlite import *
########################################################################################################################



class Role(SAFRSBase, Baseauthentication, db.Model, UserMixin):  # type: ignore
    __tablename__ = 'Role'
    _s_collection_name = 'authentication-Role'  # type: ignore
    __bind_key__ = 'authentication'

    name = Column(String(64), primary_key=True)
    allow_client_generated_ids = True

    UserRoleList = relationship('UserRole', cascade_backrefs=True, backref='Role')


class User(SAFRSBase, Baseauthentication, db.Model, UserMixin):  # type: ignore
    __tablename__ = 'User'
    _s_collection_name = 'authentication-User'  # type: ignore
    __bind_key__ = 'authentication'

    name = Column(String(128))
    notes = Column(Text)
    client_id = Column(Integer)
    id = Column(String(64), primary_key=True, unique=True)
    username = Column(String(128))
    email = Column(String(128))
    password_hash = Column(String(200))
    allow_client_generated_ids = True

    ApiList = relationship('Api', cascade_backrefs=True, backref='owner')
    UserRoleList = relationship('UserRole', cascade_backrefs=True, backref='user')
    
    # authentication-provider extension - password check
    def check_password(self, password=None):
        # print(password)
        return password == self.password_hash
    
    # authentication-provider extension - login endpoint (e.g., for swagger)

    @classmethod
    @jsonapi_rpc(valid_jsonapi=False)
    def login(cls, *args, **kwargs):
        """
            description: Login - Generate a JWT access token
            args:
                username: user
                password: password
        """
        username = kwargs.get("username", None)
        password = kwargs.get("password", None)

        user = cls.query.filter_by(id=username).one_or_none()
        if not user or not user.check_password(password):
            abort(401, "Wrong username or password")

        access_token = create_access_token(identity=user)
        return { "access_token" : access_token}


t_sqlite_sequence = Table(
    'sqlite_sequence', metadata,
    Column('name', NullType),
    Column('seq', NullType)
)


class Api(SAFRSBase, Baseauthentication, db.Model, UserMixin):  # type: ignore
    __tablename__ = 'Apis'
    _s_collection_name = 'authentication-Api'  # type: ignore
    __bind_key__ = 'authentication'

    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    connection_string = Column(String(64))
    owner_id = Column(ForeignKey('User.id'))

    # see backref on parent: owner = relationship('User', cascade_backrefs=True, backref='ApiList')


class UserRole(SAFRSBase, Baseauthentication, db.Model, UserMixin):  # type: ignore
    __tablename__ = 'UserRole'
    _s_collection_name = 'authentication-UserRole'  # type: ignore
    __bind_key__ = 'authentication'

    user_id = Column(ForeignKey('User.id'), primary_key=True)
    notes = Column(Text)
    role_name = Column(ForeignKey('Role.name'), primary_key=True)
    allow_client_generated_ids = True

    # see backref on parent: Role = relationship('Role', cascade_backrefs=True, backref='UserRoleList')
    # see backref on parent: user = relationship('User', cascade_backrefs=True, backref='UserRoleList')
