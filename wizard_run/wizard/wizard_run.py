# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

from odoo import api, models, tools

import logging
import threading

_logger = logging.getLogger(__name__)


class WizardRun(models.TransientModel):
    _name = 'wizard.run'
    _description = 'Run Method from Wizard'

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

            self.execute()
            new_cr.commit()
            new_cr.close()
            return {}

    def run(self):
        self.pre_execute()
        thread = threading.Thread(
            target=self._threaded_run,
            # Try to get xml id from context, that way it can be set
            # in button context
            args=(self.env.context.get('scheduler_cron_xml_id'), )
        )
        thread.start()
        return {
            'type': 'ir.actions.act_window_close',
        }

    def pre_execute(self):
        raise NotImplementedError("Inherit this model but override this method")

    def execute(self):
        raise NotImplementedError("Inherit this model but override this method")