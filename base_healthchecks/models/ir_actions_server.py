# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2022

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    ping_url = fields.Char('Ping URL')

    def run(self):
        hc = self.env['healthchecks.ping']
        res = False
        data = {
            "cron_running": self.env.get("cron_running", False),
            "action_names": [rec.name for rec in self],
        }
        for rec in self.filtered("ping_url"):
            hc.action_ping_start(rec.ping_url, data)
        try:
            res = super(IrActionsServer, self).run()
            for rec in self.filtered("ping_url"):
                hc.action_ping(rec.ping_url, data)
        except Exception as e:
            data["exception"] = str(e)
            for rec in self.filtered("ping_url"):
                hc.action_ping_fail(rec.ping_url, data)
            raise e
        return res

    @api.model
    def _get_eval_context(self, action=None):
        eval_context = super(IrActionsServer, self).\
            _get_eval_context(action=action)
        # Note that action should always be set for a `ir.actions.server`
        if action:
            hc = self.env['healthchecks.ping']

            def ping_log(data=False):
                if not isinstance(data, dict):
                    data = {'log': data}
                hc.action_ping_log(action.ping_url, data)

            eval_context.update({
                # helpers
                'ping_log': ping_log,
            })
        return eval_context
