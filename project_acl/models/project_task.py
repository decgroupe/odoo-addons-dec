# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

from odoo import models, api, fields


class ProjectTask(models.Model):
    _inherit = "project.task"
