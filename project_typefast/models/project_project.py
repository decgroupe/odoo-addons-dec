# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

from odoo import models


class Project(models.Model):
    _name = "project.project"
    _inherit = ["project.project", "typefast.mixin"]
