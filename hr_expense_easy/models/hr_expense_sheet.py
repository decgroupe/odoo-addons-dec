# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    @api.model
    def _get_default_name(self):
        """ Return a 'standardized' name for sheets:
            - if we are between the 11th november and the 10th december, the
                name will be: 2021/11-November
            - if we are between the 11th december and the 10th january, the
                name will be: 2021/12-December
        """
        date = fields.Date.today() - relativedelta(days=10)
        prefix = date.strftime("%Y/%m")
        if date.month == 1:
            suffix = _('January')
        elif date.month == 2:
            suffix = _('February')
        elif date.month == 3:
            suffix = _('March')
        elif date.month == 4:
            suffix = _('April')
        elif date.month == 5:
            suffix = _('May')
        elif date.month == 6:
            suffix = _('June')
        elif date.month == 7:
            suffix = _('July')
        elif date.month == 8:
            suffix = _('August')
        elif date.month == 9:
            suffix = _('September')
        elif date.month == 10:
            suffix = _('October')
        elif date.month == 11:
            suffix = _('November')
        elif date.month == 12:
            suffix = _('December')
        else:
            suffix = date.strftime("%B")

        return "%s-%s" % (prefix, suffix)

    # Override existing field definition with a default value
    name = fields.Char(default=_get_default_name, )
