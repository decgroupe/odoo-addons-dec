# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2022

import logging
from odoo import models, api, fields

_logger = logging.getLogger(__name__)


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    project_id = fields.Many2one(
        comodel_name='project.project',
        index=True,
        compute='_compute_project_id',
        store=True,
    )

    commercial_partner_id = fields.Many2one(
        related='partner_id.commercial_partner_id',
        string='Commercial Entity',
        store=True,
        related_sudo=True,
        readonly=True
    )

    @api.depends('res_model', 'res_id')
    def _compute_project_id(self):
        for obj in self:
            res_model = obj.res_model
            res_id = obj.res_id
            if not res_model or not res_id:
                _logger.error(
                    "Activity %d is missing a model/id "
                    "(res_model=%s, res_id=%d)", obj.id, res_model, res_id
                )
                continue
            if res_model == 'project.project':
                obj.project_id = res_id
            else:
                res_model_id = obj.env[res_model].search([('id', '=', res_id)])
                if 'project_id' in res_model_id._fields and \
                        res_model_id.project_id:
                    obj.project_id = res_model_id.project_id
                else:
                    obj.project_id = None
