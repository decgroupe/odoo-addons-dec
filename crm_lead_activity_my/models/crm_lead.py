# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2022

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _name = "crm.lead"
    _inherit = ["crm.lead", "mail.activity.my.mixin"]
