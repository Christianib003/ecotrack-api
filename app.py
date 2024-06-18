"""
Entry point of the application
"""

import os

from flask import Flask
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from db import db
from resources.user import blp as UserBlp
from resources.admin import blp as AdminBlp
from resources.household import blp as HouseholdBlp
from resources.collector import blp as CollectorBlp
from resources.collection_dates import blp as CollectionDatesBlp
from resources.collection_requests import blp as CollectionRequestsBlp
from models import HouseholdModel
from models import CollectorModel
from models import AdminModel


def create_app(db_url=None):
    app = Flask(__name__)

    # Configuration
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "EcoTrack API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui/api/docs"
    swagger_ui_url = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["OPENAPI_SWAGGER_UI_URL"] = swagger_ui_url
    database_uri = os.getenv("DATABASE_URL", "sqlite:///ecotrack.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate = Migrate(app, db)

    jwt = JWTManager(app)

    @jwt.additional_claims_loader
    def add_user_role_to_jwt(identity):
        # check if the user is household
        if HouseholdModel.query.filter_by(user_id=identity).first():
            return {"role": "household"}
        # check if the user is collector
        elif CollectorModel.query.filter_by(user_id=identity).first():
            return {"role": "collector"}
        # check if the user is admin
        elif AdminModel.query.filter_by(user_id=identity).first():
            return {"role": "admin"}
        # if the user is not in any of the tables, return None
        else:
            return {"role": None}

    api = Api(app)

    app.config["JWT_SECRET_KEY"] = "not-so-secret"

    # with app.app_context():
    #     db.create_all()

    # Register the blueprints
    api.register_blueprint(UserBlp)
    api.register_blueprint(AdminBlp)
    api.register_blueprint(HouseholdBlp)
    api.register_blueprint(CollectorBlp)
    api.register_blueprint(CollectionDatesBlp)
    api.register_blueprint(CollectionRequestsBlp)

    return app


app = create_app()
