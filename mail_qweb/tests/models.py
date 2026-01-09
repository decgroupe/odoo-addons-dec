from odoo import fields, models


class FakeModel(models.Model):
    _name = "fake.model"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True)

    # override to avoid having a default subject based on the name field
    def _message_compute_subject(self):
        return False


class FakeModelWithoutName(models.Model):
    _name = "fake.model.without.name"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "serial"

    serial = fields.Char(required=True)

    # override to avoid having a default subject based on the name field
    def _message_compute_subject(self):
        return False
