import base64
import logging
import os
from datetime import datetime

from flask import Flask, render_template, request
from flask_graphql import GraphQLView
import graphene

APP_NAME = "rajptRishi Internal DevOps Hub"
LEGACY_DEVOPS_TRACE_TOKEN = os.environ.get("LEGACY_DEVOPS_TRACE_TOKEN", "rjr-trace-9081")

USER_STORE = [
    {
        "id": "1",
        "username": "developer",
        "password": "DevPass123!",
        "email": "devops@rajptrishi.internal",
        "role": "developer",
        "notes": "Maintains deployment scripts and monitors CI pipelines. Trace token: rjr-trace-9081",
        "secret_note": "Uses the staging jump host during after-hours releases.",
    },
    {
        "id": "2",
        "username": "auditor",
        "password": "Audit2026?",
        "email": "auditor@rajptrishi.internal",
        "role": "auditor",
        "notes": "Audits compliance dashboards and log archives.",
        "secret_note": "Read-only access until clearance upgrade.",
    },
]


class UserSummary(graphene.ObjectType):
    username = graphene.String()
    role = graphene.String()
    email = graphene.String()


class UserDetails(graphene.ObjectType):
    username = graphene.String()
    role = graphene.String()
    email = graphene.String()
    notes = graphene.String()


class SystemHealth(graphene.ObjectType):
    timestamp = graphene.String()
    encoded_credentials = graphene.String()
    database_uri = graphene.String()


class Query(graphene.ObjectType):
    all_users = graphene.List(UserSummary)
    developer_details = graphene.Field(UserDetails)
    user_by_email = graphene.Field(UserDetails, email=graphene.String(required=True))
    system_health = graphene.Field(SystemHealth)

    def resolve_all_users(parent, info):
        return [
            {
                "username": user["username"],
                "role": user["role"],
                "email": user["email"],
            }
            for user in USER_STORE
        ]

    def resolve_developer_details(parent, info):
        return {
            "username": USER_STORE[0]["username"],
            "role": USER_STORE[0]["role"],
            "email": USER_STORE[0]["email"],
            "notes": USER_STORE[0]["notes"],
        }

    def resolve_user_by_email(parent, info, email):
        for user in USER_STORE:
            if user["email"] == email:
                return {
                    "username": user["username"],
                    "role": user["role"],
                    "email": user["email"],
                    "notes": user["notes"],
                }
        return None

    def resolve_system_health(parent, info):
        headers = info.context.get("headers", {})
        header_token = headers.get("x-devops-trace", "")
        if header_token != LEGACY_DEVOPS_TRACE_TOKEN:
            return SystemHealth(
                timestamp="denied", encoded_credentials="Access denied", database_uri=""
            )
        cred = f"{USER_STORE[0]['username']}:{USER_STORE[0]['password']}"
        encoded = base64.b64encode(cred.encode()).decode()
        return SystemHealth(
            timestamp=datetime.utcnow().isoformat(),
            encoded_credentials=encoded,
            database_uri="postgres://readonly@internal-db",
        )


schema = graphene.Schema(query=Query)


def create_app():
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    app.logger.info("Starting %s", APP_NAME)

    app.add_url_rule(
        "/graphql",
        view_func=GraphQLView.as_view(
            "graphql",
            schema=schema,
            graphiql=True,
            get_context=lambda: {"request": request.path, "headers": request.headers},
        ),
    )


    @app.route("/")
    def index():
        app.logger.info("%s served index page", request.remote_addr)
        return render_template("index.html", app_name=APP_NAME, timestamp=datetime.utcnow())

    @app.after_request
    def log_after_request(response):
        app.logger.info(
            "Handled %s %s -> %s",
            request.method,
            request.path,
            response.status_code,
        )
        return response

    return app


if __name__ == "__main__":
    PORT = int(os.environ.get("APP_PORT", 80))
    create_app().run(host="0.0.0.0", port=PORT)
