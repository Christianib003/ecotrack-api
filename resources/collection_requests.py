"""
Blueprint for handling collection requests
"""
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt

from db import db
from models import CollectionRequestModel
from models import HouseholdModel
from models import CollectorModel
from models import CollectionDateModel
from schemas import CollectionRequestSchema
from schemas import PlainUpdateCollectionRequestSchema


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

        elif jwt.get("role") == "household":
            household_id = HouseholdModel.query.filter_by(
                user_id=jwt.get("sub")).first().id
            return CollectionRequestModel.query.filter_by(
                household_id=household_id).all()
        elif jwt.get("role") == "collector":
            collector_id = CollectorModel.query.filter_by(
                user_id=jwt.get("sub")).first().id

            collector_dates = CollectionDateModel.query.filter_by(
                collector_id=collector_id).all()
            
            collector_dates_ids = [date.id for date in collector_dates]

            return CollectionRequestModel.query.filter(
                CollectionRequestModel.collection_date_id.in_(
                    collector_dates_ids)).all()

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

        household_id = HouseholdModel.query.filter_by(
            user_id=jwt.get("sub")).first().id

        collection_request = CollectionRequestModel(
            **collection_request_data,
            household_id=household_id
            )
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
    @blp.response(200, PlainUpdateCollectionRequestSchema)
    def patch(self, collection_request_id):
        """
        Update a collection request by ID

        Args:
            collection_request_id (str): The ID of the collection request
            to update

        Returns:
            dict: A dictionary containing the updated collection request

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

        data = request.get_json()
        new_status = data.get("status")
        if new_status not in ["pending", "completed"]:
            abort(400, message="Invalid status")

        collection_request = CollectionRequestModel.query.get_or_404(
            collection_request_id)
        collection_request.status = new_status

        db.session.commit()
        return collection_request

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
