# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2021

from odoo import api, fields, models


class Project(models.Model):
    _inherit = "project.project"

    partner_shipping_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_partner_shipping_id",
        string="Shipping Partner",
        readonly=True,
        store=True,
        help="Retrieved from `sale_order_id` if set, otherwise search "
        "for a sale/project name match.",
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
        store=True,
    )

    @api.depends(
        "contract_ids", "contract_ids.partner_shipping_id", "sale_order_id", "name"
    )
    def _compute_partner_shipping_id(self):
        self.partner_shipping_id = False
        for rec in self:
            if rec.contract_ids:
                contract_id = rec.contract_ids[0]
                rec.partner_shipping_id = contract_id.partner_shipping_id
            elif rec.sale_order_id:
                rec.partner_shipping_id = rec.sale_order_id.partner_shipping_id
            else:
                # fallback to search for a sale order with the same name as the project
                sale_id = self.env["sale.order"].search(
                    [("name", "=", rec.name)], limit=1
                )
                if sale_id:
                    rec.partner_shipping_id = sale_id.partner_shipping_id

    @api.depends(
        "partner_shipping_id",
        "partner_shipping_zip_id",
        "partner_id",
    )
    def _get_name_identifications(self, base_name=None):
        res = super()._get_name_identifications(base_name=base_name)
        # Add partner and its location to quickly identify a contract
        if self.partner_shipping_id:
            res.append(self.partner_shipping_id.display_name)
            # unnecessary to add the city and zip as they are already displayed in the
            # partner name by default with the 'partner_identification_base' and
            # 'partner_identification_location' modules
        elif self.partner_id:
            # Fallback to default `partner_id`
            res.append(self.partner_id.display_name)
        return res
