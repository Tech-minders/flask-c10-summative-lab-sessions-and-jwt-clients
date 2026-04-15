from marshmallow import Schema, fields, validate, validates, ValidationError

# USER SCHEMA
class UserSchema(Schema):
    id = fields.Int(dump_only=True)

    username = fields.Str(
        required=True,
        validate=validate.Length(
            min=3, 
            max=50, 
            error="Username must be between 3 and 50 characters."
        )
    )

    password = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(
            min=6, 
            error="Password must be at least 6 characters."
        )
    )

    @validates("password")
    def validate_password_not_blank(self, value, **kwargs):
        if not value or not value.strip():
            raise ValidationError("Password cannot be blank or only spaces.")

# NOTE SCHEMA
class NoteSchema(Schema):
    id = fields.Int(dump_only=True)

    title = fields.Str(
        required=True,
        validate=validate.Length(
            min=1, 
            max=100, 
            error="Title must be between 1 and 100 characters."
        )
    )

    content = fields.Str(
        required=True,
        validate=validate.Length(
            min=1, 
            error="Content cannot be empty."
        )
    )

    created_at = fields.DateTime(dump_only=True)
    user_id = fields.Int(dump_only=True)

    @validates("title")
    def validate_title_not_numbers(self, value, **kwargs):
        if value and value.strip().isdigit():
            raise ValidationError("Title cannot be only numbers.")

# SCHEMA INSTANCES
user_schema = UserSchema()
note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)
