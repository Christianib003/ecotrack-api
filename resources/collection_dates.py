"""
Blueprint for handling collection dates
"""

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt

from db import db
from models import CollectionDateModel
from schemas import CollectionDateSchema


blp = Blueprint(
    "collection_dates",
    __name__,
    description="Operations on collection dates"
)


@blp.route("/collection_dates")
class CollectionDates(MethodView):
    """
    Class for handling requests to the /collection_dates endpoint
    """
    @jwt_required()
    @blp.response(200, CollectionDateSchema(many=True))
    def get(self):
        """
        Get all collection dates in the database

        Returns:
            dict: A dictionary containing all collection dates
            in the database
        """
        jwt = get_jwt()

        user_role = jwt.get("role")

        if user_role in ("admin", "household"):
            return CollectionDateModel.query.all()

        if user_role == "collector":
            return CollectionDateModel.query.filter_by(
                collector_id=jwt.get("sub")).all()

    @jwt_required()
    @blp.arguments(CollectionDateSchema)
    @blp.response(201, CollectionDateSchema)
    def post(self, collection_date_data):
        """
        Add a new collection date to the database.

        Args:
            collection_date_data (dict): A dictionary containing the data
            for the new collection date.

        Returns:
            CollectionDateModel: The newly created collection date object.

        Raises:
            abort(400, message): If there is an error adding the collection
            date to the database.
        """
        jwt = get_jwt()

        if jwt.get("role") != "collector":
            abort(
                403,
                message="Collector privilege required to add collection dates"
                )

        collection_date = CollectionDateModel(
            **collection_date_data,
            collector_id=jwt.get("sub")
        )

        try:
            db.session.add(collection_date)
            db.session.commit()
        except SQLAlchemyError as error:
            db.session.rollback()
            abort(400, message=str(error))

        return collection_date


@blp.route("/collection_dates/<collection_date_id>")
class CollectionDate(MethodView):
    """
    Class for handling requests to the /collection_dates/<collection_date_id>
    endpoint
    """
    @jwt_required()
    @blp.response(200, CollectionDateSchema)
    def get(self, collection_date_id):
        """
        Get a collection date by ID

        Args:
            collection_date_id (str): ID of the collection date to retrieve

        Returns:
            tuple: A tuple containing the collection date and the HTTP
            status code 200
        """
        jwt = get_jwt()
        if jwt.get("role") in ("collector", "admin"):
            return CollectionDateModel.query.get_or_404(collection_date_id)

        abort(
            403,
            message="Collector privileges required to view collection dates"
            )

    @jwt_required()
    def delete(self, collection_date_id):
        """
        Delete a collection date by ID

        Args:
            collection_date_id (str): The ID of the collection date to delete

        Returns:
            dict: A dictionary containing a message indicating the success of
            the deletion

        Raises:
            NotFound: If the collection date with the specified ID
            does not exist

        """
        jwt = get_jwt()
        if jwt.get("role") != "admin":
            abort(
                403,
                message="Admin privileges required to delete collection dates"
                )

        collection_date = CollectionDateModel.query.get_or_404(
            collection_date_id)
        db.session.delete(collection_date)
        db.session.commit()

        return {"message": "Collection date deleted successfully."}
