# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jun 2021

from odoo import fields, models, api


class ResPartnerTrainingSpecialty(models.Model):
    _description = 'Educational Training Specialty'
    _name = "res.partner.training.specialty"
    _order = "name"
    _rec_name = 'complete_name'

    active = fields.Boolean(
        'Active',
        default=True,
    )
    name = fields.Char(
        'Name',
        required=True,
        translate=False,
    )
    complete_name = fields.Char(
        'Complete Name',
        compute='_compute_complete_name',
        store=True,
    )
    acronym = fields.Char(
        'Acronym',
        translate=False,
    )
    training_id = fields.Many2one(
        'res.partner.training',
        string='Educational Training',
        required=True,
    )

    _sql_constraints = [
        (
            'train_name_uniq', 'unique(training_id, name)',
            'Name must be unique !'
        ),
        (
            'train_acro_uniq', 'unique(training_id, acronym)',
            'Acronym must be unique !'
        ),
    ]

    @api.depends('name', 'acronym', 'training_id')
    def _compute_complete_name(self):
        for rec in self:
            if rec.acronym:
                suffix = rec.acronym
            else:
                suffix = rec.name
            rec.complete_name = "{} {}".format(rec.training_id.name, suffix)
