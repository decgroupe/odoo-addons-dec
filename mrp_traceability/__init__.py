from . import models

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    """This hook is used to ..."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["stock.move"]._migrate_dest_move_to_conv_dest_move()
