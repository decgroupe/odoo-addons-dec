# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2022

from odoo import api, models, _, fields, SUPERUSER_ID


class ProductionStage(models.Model):
    _name = 'mrp.production.stage'
    _description = 'Production Stage'
    _order = 'sequence, id'

    name = fields.Char(
        string='Stage Name',
        required=True,
        translate=True,
    )
    code = fields.Char(
        string='Code',
        required=True,
        help="Unique lowercase string identifier",
    )
    emoji = fields.Char(
        string='Icon',
        translate=False,
    )
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=1)
    fold = fields.Boolean(
        string='Folded in Kanban',
        help='This stage is folded in the kanban view when there are no '
        'records in that stage to display.'
    )
    todo = fields.Boolean(
        string="To-do",
        help="This stage is considered to have actions needed",
    )
    activity_type_id = fields.Many2one(
        comodel_name="mail.activity.type",
        string="Activity Type",
    )

    _sql_constraints = [
        ('code_uniq', 'unique (code)', "Code must be unique !"),
    ]

    @api.depends('name', 'emoji')
    def name_get(self):
        res = []
        for rec in self:
            if rec.emoji:
                name = '%s %s' % (rec.emoji, rec.name)
            else:
                name = rec.name
            res.append((rec.id, name))
        return res
