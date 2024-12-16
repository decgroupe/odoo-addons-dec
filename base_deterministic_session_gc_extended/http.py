# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2024

import logging
import time
from datetime import datetime

from odoo import http
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, config

_logger = logging.getLogger(__name__)


if hasattr(http, "deterministic_session_gc"):
    old_deterministic_session_gc = http.deterministic_session_gc
else:
    old_deterministic_session_gc = None


def deterministic_session_gc(session_store, session_expiry_delay=None):
    if session_expiry_delay is None:
        session_expiry_delay = config.get("session_expiry_delay", 60 * 60 * 24 * 7)
    expired_time = time.time() - int(session_expiry_delay)
    _logger.debug(
        "Deleting all sessions inactive since %s",
        datetime.fromtimestamp(expired_time).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
    )
    http.session_gc_process(session_store, expired_time)


if "base_deterministic_session_gc" in config.get("server_wide_modules"):
    _logger.debug("Disabling default deterministic_session_gc")
    http.deterministic_session_gc = deterministic_session_gc
