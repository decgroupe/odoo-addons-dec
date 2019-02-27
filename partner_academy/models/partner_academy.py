# -*- encoding: utf-8 -*-

import time

from osv import fields
from osv import osv



class res_partner_academy(osv.osv):
    """ Description """

    _name = 'res.partner.academy'
    _description = 'Academy'
    _rec_name = 'name'

    _columns = {     
        'name': fields.text('Name', required=True),
    }

    _defaults = {

    }
 
    _order = 'name'

res_partner_academy()


