# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2022


def set_view_mode_first(views: list, mode: str) -> str:
    """When returning an action fetched from database, the view order
    cannot be easilly modified. This function is a shortcut to change
    view priority and move a specific mode first.

    Args:
        views (list): list of tuples mapped like (`view_id`, `view_mode`)
        mode (str): name of mode (`list`, `kanban`, `form`, ...) to move
        first in views definition

    Returns:
        list: `views` reordered
    """
    res = []
    for definition in views:
        view_id, view_mode = definition
        if view_mode == mode:
            res.insert(0, definition)
        else:
            res.append(definition)
    return res
