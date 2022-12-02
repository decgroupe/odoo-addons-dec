# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2022


from odoo import models, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    def __init__(self, pool, cr):
        """ Override of __init__ to add access rights on new fields.
            Access rights are disabled by default, but allowed
            on some specific fields defined in
            self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        init_res = super().__init__(pool, cr)
        type(self).SELF_WRITEABLE_FIELDS = list(
            set(
                self.SELF_WRITEABLE_FIELDS + [
                    'auto_subscribe_on_tag',
                    'auto_subscribe_on_message',
                    'auto_subscribe_on_activity',
                ]
            )
        )
        return init_res
