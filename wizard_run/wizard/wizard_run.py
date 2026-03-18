# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

import logging
import threading

from odoo import models

_logger = logging.getLogger(__name__)


class WizardRun(models.TransientModel):
    _name = "wizard.run"
    _description = "Run Method from Wizard"

    def _threaded_run(self):
        with self.env.registry.cursor() as new_cr:
            # As this function is in a new thread, we need to open a new
            # cursor, because the old one may be closed
            self = self.with_env(self.env(cr=new_cr))
            try:
                self.execute()
                new_cr.commit()
            except Exception as e:
                _logger.info("Attempt to execute aborted: %s", e)
                new_cr.rollback()
            finally:
                new_cr.close()
            return {}

    def run(self):
        self.pre_execute()
        thread = threading.Thread(target=self._threaded_run)
        thread.start()
        return {
            "type": "ir.actions.act_window_close",
        }

    def pre_execute(self):
        raise NotImplementedError("Inherit this model but override this method")

    def execute(self):
        raise NotImplementedError("Inherit this model but override this method")
