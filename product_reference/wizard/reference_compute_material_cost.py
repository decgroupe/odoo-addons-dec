# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2020

from odoo import api, models, tools

import logging
import threading

_logger = logging.getLogger(__name__)


class ReferenceComputeMaterialCost(models.TransientModel):
    _name = 'reference.compute_material_cost'
    _description = 'Compute Material Cost Manually'

    def _threaded_run(self, scheduler_cron_xml_id=False):
        with api.Environment.manage():
            # As this function is in a new thread, we need to open a new
            # cursor, because the old one may be closed
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            if scheduler_cron_xml_id:
                scheduler_cron = self.sudo().env.ref(scheduler_cron_xml_id)
                # Avoid to run the scheduler multiple times in the same time
                try:
                    with tools.mute_logger('odoo.sql_db'):
                        self._cr.execute(
                            "SELECT id FROM ir_cron WHERE id = %s FOR UPDATE NOWAIT",
                            (scheduler_cron.id, )
                        )
                except Exception:
                    _logger.info('Attempt to run aborted, as already running')
                    self._cr.rollback()
                    self._cr.close()
                    return {}

            self.env['ref.reference'].run_material_cost_scheduler(
                # use_new_cursor=self._cr.dbname, company_id=company.id
            )
            new_cr.close()
            return {}

    def run(self):
        thread = threading.Thread(target=self._threaded_run, args=())
        thread.start()
        return {
            'type': 'ir.actions.act_window_close',
        }
