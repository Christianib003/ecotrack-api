"""
Blueprint for handling collection requests
"""

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt

from db import db
from models import CollectionRequestModel
from schemas import CollectionRequestSchema


blp = Blueprint(
    "collection_requests",
    __name__,
    description="Operations on collection requests"
)


@blp.route("/collection_requests")
class CollectionRequests(MethodView):
    """
    Class for handling requests to the /collection_requests endpoint
    """
    @jwt_required()
    @blp.response(200, CollectionRequestSchema(many=True))
    def get(self):
        """
        Get all collection requests in the database

        Returns:
            dict: A dictionary containing all collection requests in
            the database
        """
        jwt = get_jwt()
        if jwt.get("role") == "admin":
            return CollectionRequestModel.query.all()
        elif jwt.get("role") in ("household", "collector"):
            return CollectionRequestModel.query.filter_by(
                household_id=jwt.get("sub")).all()

        abort(
            403,
            message="Admin/household privileges required to access resources"
            )

    @jwt_required()
    @blp.arguments(CollectionRequestSchema)
    @blp.response(201, CollectionRequestSchema)
    def post(self, collection_request_data):
        """
        Add a new collection request to the database

        Args:
            collection_request_data (dict): A dictionary containing the
            data for the new collection request

        Returns:
            dict: A dictionary containing the newly created collection request

        Raises:
            abort(400, message): If there is an error adding the collection
            request to the database
        """
        jwt = get_jwt()
        if jwt.get("role") != "household":
            abort(
                403,
                message="Household privileges required to access resources"
                )

        collection_request = CollectionRequestModel(**collection_request_data)
        try:
            db.session.add(collection_request)
            db.session.commit()
        except SQLAlchemyError as error:
            db.session.rollback()
            abort(400, message=str(error))

        return collection_request


@blp.route("/collection_requests/<collection_request_id>")
class CollectionRequest(MethodView):
    """
    Class for handling requests to the
    /collection_requests/<collection_request_id> endpoint
    """
    @jwt_required()
    @blp.response(200, CollectionRequestSchema)
    def get(self, collection_request_id):
        """
        Get a collection request by ID

        Args:
            collection_request_id (str): The ID of the collection request
                to retrieve

        Returns:
            dict: A dictionary containing the requested collection request

        Raises:
            NotFound: If the collection request with the given ID does
            not exist
        """
        return CollectionRequestModel.query.get_or_404(collection_request_id)

    @jwt_required()
    def delete(self, collection_request_id):
        """
        Delete a collection request by ID

        Args:
            collection_request_id (str): The ID of the collection request
            to delete

        Returns:
            dict: A dictionary containing a message indicating the success
            of the deletion

        Raises:
            NotFound: If the collection request with the given ID does
            not exist
        """
        jwt = get_jwt()
        if jwt.get("role") != "household":
            abort(
                403,
                message="Household privilege required to do this action"
                )

        collection_request = CollectionRequestModel.query.get_or_404(
            collection_request_id)
        db.session.delete(collection_request)
        db.session.commit()
        return {"message": "Collection request deleted successfully."}
