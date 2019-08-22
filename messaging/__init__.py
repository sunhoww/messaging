# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask_restful import Api
from flask_graphql import GraphQLView
from flask_jwt_extended import JWTManager, jwt_optional

from messaging.resources.accounts import Account, AccountList, AccountKey
from messaging.resources.providers import (
    Provider,
    ProviderList,
    ProviderMethod,
    ProviderMethodPut,
    ProviderConfigPut,
)
from messaging.resources.services import (
    Service,
    ServiceList,
    ServiceAll,
    ServiceStaticPut,
    ServiceStatic,
    ServiceAction,
    ServiceBalance,
)
from messaging.resources.messages import MessageList, MessageAll
from messaging.exceptions import errors
from messaging.schema import schema


import requests_toolbelt.adapters.appengine

requests_toolbelt.adapters.appengine.monkeypatch()

env = (
    "prod"
    if os.getenv("SERVER_SOFTWARE", "").startswith("Google App Engine/")
    else "dev"
)


app = Flask(__name__)
app.config.from_object("settings.{env}.FlaskConfig".format(env=env))

jwt = JWTManager(app)


@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    return {"site": identity.site}


@jwt.user_identity_loader
def make_identity_for_access_token(identity):
    return identity.uid


api = Api(app, errors=errors)

api.add_resource(AccountList, "/accounts")
api.add_resource(Account, "/accounts/<string:id>")
api.add_resource(AccountKey, "/accounts/<string:id>/key")
api.add_resource(ProviderList, "/providers")
api.add_resource(Provider, "/providers/<string:id>")
api.add_resource(ProviderMethodPut, "/providers/<string:id>/methods")
api.add_resource(ProviderMethod, "/providers/<string:id>/methods/<string:action>")
api.add_resource(ProviderConfigPut, "/providers/<string:id>/config")
api.add_resource(ServiceList, "/accounts/<string:site>/services")
api.add_resource(ServiceAll, "/services")
api.add_resource(Service, "/services/<string:id>")
api.add_resource(ServiceStaticPut, "/services/<string:id>/static")
api.add_resource(ServiceStatic, "/services/<string:id>/static/<string:field>")
api.add_resource(ServiceBalance, "/services/<string:id>/balance")
api.add_resource(MessageList, "/services/<string:service>/messages")
api.add_resource(ServiceAction, "/services/<string:id>/<string:action>")
api.add_resource(MessageAll, "/messages")

view_func = GraphQLView.as_view("graphql", schema=schema, graphiql=False)

app.add_url_rule("/graphql", view_func=jwt_optional(view_func))
