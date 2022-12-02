# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import models, api, fields


class Meeting(models.Model):
    _inherit = 'calendar.event'

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None
    ):
        instance = self
        if self._context.get('reservable'):
            if self._context.get('mymeetings'):
                args += [
                    ('|'),
                    ('partner_ids', 'in', self.env.user.partner_id.ids),
                    ('partner_ids.function', 'ilike', "reservable"),
                ]
                instance = self.with_context(mymeetings=False)
            else:
                args += [('partner_ids.function', 'ilike', "reservable")]

        return super(Meeting, instance)._search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid
        )
