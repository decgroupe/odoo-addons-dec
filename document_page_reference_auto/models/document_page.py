# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

import re
import string

from odoo import models, fields, api


class DocumentPage(models.Model):
    _inherit = 'document.page'

    @api.onchange('name')
    def on_name_change(self):
        if self.name and not self.reference:
            res = 'page_'
            parts = re.split(r"'|,| ", self.name)
            for part in parts:
                for letter in part:
                    if letter.lower() in string.ascii_lowercase:
                        res += letter.lower()
                        break
            self.reference = res
