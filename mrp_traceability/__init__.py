from . import models


def post_init_hook(env):
    env["stock.move"]._migrate_dest_move_to_conv_dest_move()
