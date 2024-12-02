from odoo import fields, models


class FakeModel(models.Model):
    _name = "fake.model"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True)


class FakeModelWithoutName(models.Model):
    _name = "fake.model.without.name"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "serial"

    serial = fields.Char(required=True)
