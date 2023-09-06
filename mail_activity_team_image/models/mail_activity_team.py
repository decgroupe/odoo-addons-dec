# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2023

from odoo import models


class MailActivityTeam(models.Model):
    _name = "mail.activity.team"
    _inherit = ["mail.activity.team", "image.mixin"]
