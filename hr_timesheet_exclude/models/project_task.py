# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    exclude_from_timesheet = fields.Boolean(
        string='Exclude from Timesheet Accounting',
        default=False,
        help=(
            "Checking this would exclude any timesheet entries logged towards "
            "this project in Analysis view."
        ),
    )
