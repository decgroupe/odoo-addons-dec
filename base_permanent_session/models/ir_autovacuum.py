# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2024

import logging
import os
from pathlib import Path

from odoo import api, http, models

_logger = logging.getLogger(__name__)


class AutoVacuum(models.AbstractModel):
    _inherit = "ir.autovacuum"

    @api.model
    def maintain_permanent_sessions(self):
        store = http.root.session_store
        for sid in store.list():
            session = store.get(sid)
            if not session.db == self.env.cr.dbname:
                continue
            if session.session_token and session.permanent:
                session_filename = store.get_session_filename(sid)
                store.save(session)
                # use touch instead of `store.save(session)` to speed-up process
                # Path(session_filename).touch()
                _logger.debug(
                    "Session %s updated (%s)",
                    session_filename,
                    os.path.getmtime(session_filename),
                )
        return True
