"""
This file contains the schema for the various models.
"""

from marshmallow import Schema, fields


class PlainUserSchema(Schema):
    """
    This schema represents a user with no relationships.
    """
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class PlainAdminSchema(Schema):
    """
    This schema represents an admin.
    """
    id = fields.Int(dump_only=True)


class PlainHouseholdSchema(Schema):
    """
    This schema represents a household.
    """
    id = fields.Int(dump_only=True)
    house_number = fields.Str(required=True)
    area = fields.Str(required=True)


class PlainCollectorSchema(Schema):
    """
    This schema represents a collector.
    """
    id = fields.Int(dump_only=True)
    allocated_area = fields.Str(required=True)


class PlainCollectionDateSchema(Schema):
    """
    This schema represents a collection date.
    """
    id = fields.Int(dump_only=True)
    collection_date = fields.Date(required=True)


class PlainCollectionRequestSchema(Schema):
    """
    This schema represents a collection request.
    """
    id = fields.Int(dump_only=True)
    status = fields.Str(missing="pending")
    amount = fields.Float(required=True)


class UserSchema(PlainUserSchema):
    """
    This schema represents a user with relationships.
    """
    household = fields.Nested(PlainHouseholdSchema(), dump_only=True)
    collector = fields.Nested(PlainCollectorSchema(), dump_only=True)
    admin = fields.Nested(PlainAdminSchema(), dump_only=True)


class AdminSchema(PlainAdminSchema):
    """
    This schema represents an admin with relationships.
    """
    user_id = fields.Int(dump_only=True)


class CollectionRequestSchema(PlainCollectionRequestSchema):
    """
    This schema represents a collection request with relationships.
    """
    collection_date_id = fields.Int(required=True, load_only=True)
    household = fields.Nested(PlainHouseholdSchema(), dump_only=True)
    collection_date = fields.Nested(
        PlainCollectionDateSchema(), dump_only=True)


class CollectionDateSchema(PlainCollectionDateSchema):
    """
    This schema represents a collection date with relationships.
    """
    collection_requests = fields.List(fields.Nested(
        PlainCollectionRequestSchema()), dump_only=True)


class HouseholdSchema(PlainHouseholdSchema):
    """
    This schema represents a household with relationships.
    """
    user_id = fields.Int(dump_only=True)
    collection_requests = fields.List(fields.Nested(
        PlainCollectionRequestSchema()), dump_only=True)


class CollectorSchema(PlainCollectorSchema):
    """
    This schema represents a collector with relationships.
    """
    user_id = fields.Int(dump_only=True)
    collection_dates = fields.List(fields.Nested(
        PlainCollectionDateSchema()), dump_only=True)
