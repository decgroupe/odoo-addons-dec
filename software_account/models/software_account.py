# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class SoftwareAccount(models.Model):
    _name = "software.account"
    _description = "Software Account"
    _rec_name = "login"
    _order = "id desc"

    supplier_id = fields.Many2one(
        comodel_name="software.account.supplier",
        string="Supplier",
        required=True,
    )
    login = fields.Char(
        string="Login",
        size=64,
        required=True,
    )
    password = fields.Char(
        string="Password",
        size=64,
        required=True,
    )
    email = fields.Char(
        string="E-Mail",
        size=64,
        required=True,
    )
    firstname = fields.Char(
        string="Firstname",
        size=64,
    )
    lastname = fields.Char(
        string="Lastname",
        size=64,
    )
    question = fields.Text(
        string="Question",
    )
    answer = fields.Text(
        string="Answer",
    )
    pin = fields.Char(
        string="Pin Code",
        size=16,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        domain=[],
        change_default=True,
    )
    production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Production",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
    )
    datetime = fields.Datetime(
        string="Modification date",
        default=fields.Datetime.now,
    )
    info = fields.Text(
        string="Informations",
    )

    def _get_aeroo_report_filename(self):
        names = [x.login or str(x.id) for x in self]
        res = "-".join(names)
        return res
