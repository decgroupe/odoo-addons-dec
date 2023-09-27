# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class ResPartnerAcademy(models.Model):
    """National Education Academy"""

    _name = "res.partner.academy"
    _description = "Academy"
    _rec_name = "name"
    _order = "name"

    active = fields.Boolean(
        default=True,
        help="Set active to false to hide the Academy without removing it.",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Rectorate",
    )
    name = fields.Text(
        string="Name",
        required=True,
    )
    email_domain = fields.Char(
        help="Filling this domain (part after the @) will help to "
        "quickly identify a partner academy using its e-mail suffix."
        "Please note that multiple domains can be added (separated by a single-space)."
    )
    logo = fields.Binary(
        related="partner_id.image_1920",
        string="Academy Logo",
        readonly=False,
    )
    state_id = fields.Many2one(
        comodel_name="res.country.state",
        related="partner_id.state_id",
        string="State",
        readonly=False,
    )
    country_id = fields.Many2one(
        comodel_name="res.country",
        related="partner_id.country_id",
        string="Country",
    )
    department_ids = fields.Many2many(
        comodel_name="res.country.department",
        string="Departments",
        help="Departments of this academy",
        domain="[('country_id', '=', country_id), ('state_id', '=', state_id)]",
    )
