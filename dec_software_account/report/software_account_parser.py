import time
from datetime import datetime, timedelta
from dateutil.rrule import *
from dateutil.relativedelta import relativedelta
from report import report_sxw
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from tools.translate import _


class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'picking': self.get_picking,
        })
        self.context = context

    def get_picking(self, data):
        if data.has_key('form') and data['form'].has_key('picking'):
            return data['form']['picking']
        else:
            return True
