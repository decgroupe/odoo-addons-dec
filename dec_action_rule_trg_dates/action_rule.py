# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher (Camptocamp) 
#    Contributor: 
#    Copyright 2011 Camptocamp SA
#    Donors:
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import fields, osv
from tools.translate import _ 
from datetime import datetime, timedelta

def get_datetime(date_field):
    '''redefining get_datetime as it is out of scope with a little improvment'''
    # complete date time if date_field contains only a date
    date_split = date_field.split(' ')
    if len(date_split) == 1:
        date_field = date_split[0] + " 00:00:00"
    return datetime.strptime(date_field[:19], '%Y-%m-%d %H:%M:%S')


class ActionRule(osv.osv):

    _inherit = 'base.action.rule'

    _columns = {
        'trg_date_id': fields.many2one('ir.model.fields',
                                       'Trigger Date',
                                       domain="[('model_id', '=', model_id),"
                                               "('ttype','in',('date','datetime'))]"),
    }

    def pre_action(self, cr, uid, ids, model, context=None):
        """
        change trg_date_type by trg_date_id
        """
        # Searching for action rules
        cr.execute("SELECT model.model, rule.id  FROM base_action_rule rule \
                        LEFT JOIN ir_model model on (model.id = rule.model_id) \
                        WHERE active")
        res = cr.fetchall()
        # Check if any rule matching with current object
        for obj_name, rule_id in res:
            if not (model == obj_name):
                continue
            else:
                obj = self.pool.get(obj_name)
                # If the rule doesn't involve a time condition, run it immediately
                # Otherwise we let the scheduler run the action
                if not self.browse(cr, uid, rule_id, context=context).trg_date_id:
                    self._action(cr, uid, [rule_id], obj.browse(cr, uid, ids, context=context), context=context)
        return True


    def _check(self, cr, uid, automatic=False, use_new_cursor=False, \
                       context=None):
        """
        Rewrite of the function called by scheduler.
        Nested loops make it impossible to modify in a clean way

        Use trg_date_id instead of trg_date_type
        This method can be used for any field date
        """
        rule_pool = self.pool.get('base.action.rule')
        rule_ids = rule_pool.search(cr, uid, [], context=context)
        self._register_hook(cr, uid, rule_ids, context=context)

        rules = self.browse(cr, uid, rule_ids, context=context)
        for rule in rules:
            model = rule.model_id.model
            model_pool = self.pool.get(model)
            last_run = False
            if rule.last_run:
                last_run = get_datetime(rule.last_run)
            now = datetime.now()
            for obj_id in model_pool.search(cr, uid, [], context=context):
                obj = model_pool.browse(cr, uid, obj_id, context=context)
                # Calculate when this action should next occur for this object
                base = False
                if rule.trg_date_id:
                    date_type = rule.trg_date_id.name
                    if (date_type=='date_action_last'
                            and hasattr(obj, 'create_date')):
                        if hasattr(obj, 'date_action_last') and obj.date_action_last:
                            base = obj.date_action_last
                        else:
                            base = obj.create_date
                    elif (hasattr(obj, date_type)
                         and obj.read([date_type])[0][date_type]):
                        base = obj.read([date_type])[0][date_type]
                if base:
                    fnct = {
                        'minutes': lambda interval: timedelta(minutes=interval),
                        'day': lambda interval: timedelta(days=interval),
                        'hour': lambda interval: timedelta(hours=interval),
                        'month': lambda interval: timedelta(months=interval),
                    }
                    base = get_datetime(base)
                    delay = fnct[rule.trg_date_range_type](rule.trg_date_range)
                    action_date = base + delay
                    if (not last_run or (last_run <= action_date < now)):
                        self._action(cr, uid, [rule.id], [obj], context=context)
            rule_pool.write(cr, uid, [rule.id], {'last_run': now},
                            context=context)
            

    def do_check(self, cr, uid, action, obj, context=None):
        if action.trg_date_id:
            # Ignore action with a date as trigger as they will be checked by the scheduler
            return False
        else:
            res = super(ActionRule, self).do_check(cr, uid, action, obj, context=context)
            return res

ActionRule()
