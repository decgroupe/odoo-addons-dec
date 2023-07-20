# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2021

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    partner_shipping_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_partner_shipping_id",
        string="Shipping Partner",
        readonly=True,
        store=True,
    )
    partner_shipping_zip_id = fields.Many2one(
        comodel_name="res.city.zip",
        related="partner_shipping_id.zip_id",
        string="Shipping Partner's ZIP",
        readonly=True,
        store=True,
    )
    partner_shipping_country_id = fields.Many2one(
        comodel_name="res.country",
        related="partner_shipping_id.country_id",
        string="Shipping Partner's Country",
        readonly=True,
        store=True,
    )

    @api.depends("sale_order_id", "sale_order_id.partner_shipping_id", "production_id")
    def _compute_partner_shipping_id(self):
        # Note that we don't need to depends on `sale_line_id` as the
        # `sale_order_id` is already computed from it
        for rec in self:
            if rec.sale_order_id:
                rec.partner_shipping_id = rec.sale_order_id.partner_shipping_id
            elif rec.production_id:
                rec.partner_shipping_id = rec.production_id.partner_id
            else:
                rec.partner_shipping_id = False
