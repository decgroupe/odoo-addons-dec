import logging

_logger = logging.getLogger(__name__)

try:
    from openupgradelib import openupgrade
except (ImportError, IOError) as err:
    _logger.debug(err)


def rename_module(cr):
    openupgrade.update_module_names(
        cr,
        [("mrp_stock_cancel", "mrp_stock_actions")],
        merge_modules=True,
    )
