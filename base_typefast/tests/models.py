from odoo import fields, models


class FakeModel(models.Model):
    _inherit = ["typefast.mixin"]
    _name = "fake.model"

    name = fields.Char(required=True)
    value = fields.Integer()


class FakeModelCharName(models.Model):
    _inherit = ["typefast.mixin"]
    _name = "fake.model.char.name"
    _rec_name = "serial"

    serial = fields.Char(required=True)


class FakeModelIntName(models.Model):
    _inherit = ["typefast.mixin"]
    _name = "fake.model.int.name"
    _rec_name = "number"

    number = fields.Integer(required=True)


class FakeModelM2oName(models.Model):
    _inherit = ["typefast.mixin"]
    _name = "fake.model.m2o.name"
    _rec_name = "partner_id"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        required=True,
        index=True,
    )


class FakeModelCustomNameGet(models.Model):
    _inherit = ["typefast.mixin"]
    _name = "fake.model.custom.name.get"
    _typefast_options = {
        "source": "name_get",
    }

    name = fields.Char(required=True)
    prefix = fields.Char(required=True)
    suffix = fields.Char(required=True)

    def name_get(self):
        result = []
        for rec in self:
            name = "%s %s %s" % (rec.prefix, rec.name, rec.suffix)
            result.append((rec.id, name))
        return result
