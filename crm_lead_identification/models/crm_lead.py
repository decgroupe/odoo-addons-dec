# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

import logging

from odoo import fields, api, models

_logger = logging.getLogger(__name__)

SEARCH_SEPARATOR = ' →'


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if SEARCH_SEPARATOR in name:
            name = name.partition(SEARCH_SEPARATOR)[0]
        names = super(CrmLead, self.with_context(
            name_search=True
        )).name_search(name=name, args=args, operator=operator, limit=limit)
        return names

    @api.multi
    def name_get(self):
        if self.env.context.get('name_search'):
            return self.name_get_from_search()
        else:
            return super().name_get()

    @api.multi
    @api.depends('number', 'name')
    def name_get_from_search(self):
        """ Custom naming to quickly identify a lead
        """
        res = []
        for rec in self:
            identification = ' '.join(rec._get_name_identifications())
            name = '[%s] %s%s %s' % (
                rec.number, rec.name, SEARCH_SEPARATOR, identification
            )
            if rec.stage_id and not rec.stage_id.name[0].isalpha():
                emoji = rec.stage_id.name[0]
                name = '%s %s' % (emoji, name)
            res.append((rec.id, name))
        return res

    @api.multi
    @api.depends('partner_id.name', 'partner_zip_id')
    def _get_name_identifications(self):
        self.ensure_one()
        res = []
        if self.partner_id:
            res.append(
                '%s %s' % (
                    self.partner_id._get_contact_type_emoji(),
                    self.partner_id.display_name
                )
            )
        if self.partner_zip_id:
            res.append('🗺️ %s' % (self.partner_zip_id.display_name))
        return res

    @api.multi
    @api.depends('partner_zip_id', 'partner_zip_id.name')
    def _compute_names(self):
        super()._compute_names()
        for rec in self:
            if rec.partner_zip_id:
                rec.search_name = "{} {}".format(
                    rec.search_name, rec.partner_zip_id.display_name
                )
