"""
This module contains the model for the collection_request table
in the database.
"""

from db import db


class CollectionRequestModel(db.Model):
    """
    Class representing the collection_request table in the database.

    Attributes:
        id (int): The primary key of the collection request.
        status (str): The status of the collection request.
        household_id (int): The foreign key referencing the households table.
        collection_date_id (int): The foreign key referencing the
        collection_dates table.
        household (HouseholdModel): The relationship to the HouseholdModel.
        collection_date (CollectionDateModel): The relationship to the
        CollectionDateModel.
    """

    __tablename__ = "collection_requests"

    id = db.Column(
        db.Integer,
        primary_key=True
        )
    status = db.Column(
        db.String(80),
        nullable=False
        )
    amount = db.Column(
        db.Float,
        nullable=False
    )
    household_id = db.Column(
        db.Integer,
        db.ForeignKey("households.id"),
        nullable=False
        )
    collection_date_id = db.Column(
        db.Integer,
        db.ForeignKey("collection_dates.id"),
        nullable=False
        )
    household = db.relationship(
        "HouseholdModel",
        back_populates="collection_requests"
        )
    collection_date = db.relationship(
        "CollectionDateModel",
        back_populates="collection_requests"
        )
