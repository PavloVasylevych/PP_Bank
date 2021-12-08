from marshmallow import Schema, fields
from marshmallow.validate import Length, Range

class UserSchema(Schema):
    username = fields.String(validate=Length(min=3))
    password = fields.String(validate=Length(min=3))
    ClientName = fields.String(validate=Length(min=3))
    firstName = fields.String(validate=Length(min=3))
    lastName = fields.String(validate=Length(min=3))
    status = fields.String(validate=Length(min=3))

class BalanceSchema(Schema):
    name = fields.String(validate=Length(min=3))
    balance = fields.Integer(strict=True)

class CreditSchema(Schema):
    id_borrower = fields.Integer(strict=True)
    id_bank = fields.Integer(strict=True)
    loan_status = fields.Integer(strict=True, validate=Range(min=0, max=1))
    loan_date = fields.String(validate=Length(min=3))
    loan_amount = fields.Integer(strict=True)
    interest_rate = fields.Integer(strict=True)
