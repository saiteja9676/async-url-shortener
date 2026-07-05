from marshmallow import Schema, fields

class URLSchema(Schema):
    url = fields.Url(
        required=True,
        error_messages={
            "required":"URL is required",
            "invalid":"Not a valid URL"
        }
    )