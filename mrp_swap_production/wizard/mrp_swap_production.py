# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2021

import logging
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


def _logger_print(*args):
    _logger.info(' '.join(str(x) for x in list(args)))


class MrpSwapProduction(models.TransientModel):
    _name = 'mrp.swap.production'
    _description = 'Swap two manufacturing orders'

    this_production_id = fields.Many2one(
        'mrp.production',
        'This',
        required=True,
        readonly=True,
        domain=[],
    )
    product_id = fields.Many2one(
        related='this_production_id.product_id',
        string='Product',
        required=True,
        readonly=True,
    )
    other_production_id = fields.Many2one(
        'mrp.production',
        'Other',
        required=True,
        readonly=False,
    )
    swap_line_ids = fields.Many2many(
        'mrp.swap.production.line',
        string='Swap Lines',
    )

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        return rec

    @api.onchange('other_production_id')
    def onchange_other_production_id(self):
        mapping = {}
        self.swap_line_ids.unlink()
        if not self.other_production_id:
            return

        def _map_subproduction_with_product(production_id):
            sub_production_ids = production_id.move_raw_ids\
                .mapped('move_orig_ids').mapped('production_id')
            for p in sub_production_ids:
                if not p.product_id in mapping:
                    mapping[p.product_id] = []
                mapping[p.product_id].append(p)

        _map_subproduction_with_product(self.this_production_id)
        _map_subproduction_with_product(self.other_production_id)

        # Pre-Fill main line
        vals = {
            'product_id': self.product_id.id,
            'from_production_id': self.this_production_id.id,
            'to_production_id': self.other_production_id.id,
            'swap_final_moves': True,
        }
        line_ids = self.env['mrp.swap.production.line'].create(vals)

        for product_id, production_ids in mapping.items():
            if len(production_ids) == 2:
                vals = {
                    'product_id': product_id.id,
                    'from_production_id': production_ids[0].id,
                    'to_production_id': production_ids[1].id,
                }
                line_ids += self.env['mrp.swap.production.line'].create(vals)
        self.swap_line_ids += line_ids

    @api.model
    def _get_fields_that_must_be_identical(self):
        return {
            'mrp.production':
                [
                    'product_id',
                    'product_qty',
                    'product_uom_id',
                    'allow_timesheets',
                ],
            'mrp.production.request': [
                'product_qty',
                'product_uom_id',
            ],
        }

    @api.model
    def log_field(self, name, obj):
        cache_value = obj[name]
        if isinstance(cache_value, models.Model):
            for value in cache_value:
                _logger_print('-', name, value, value.name_get())
        else:
            _logger_print(name, cache_value)

        if not cache_value:
            _logger_print(name, 'is empty', cache_value)

    @api.model
    def swap_fields(self, name, this, other):
        if this[name] == other[name]:
            _logger_print(name, 'are equals ->', this[name])
            return

        _logger_print('Field value before:')
        self.log_field(name, this)
        self.log_field(name, other)

        # Cache value to assign ...
        cache_this_value = this[name]
        cache_other_value = other[name]

        # ... and set them
        this[name] = cache_other_value
        other[name] = cache_this_value

        _logger_print('Field value after:')
        self.log_field(name, this)
        self.log_field(name, other)

    def swap_production(self, moa_id, mob_id, swap_final_moves=False):
        _logger_print(
            'Swaping',
            moa_id.name_get(),
            'as THIS with',
            mob_id.name_get(),
            'as OTHER',
        )

        for field in self._get_fields_that_must_be_identical(
        )['mrp.production']:
            if moa_id[field] != mob_id[field]:
                raise Exception(_('%s must be the same') % (field))

        self.swap_fields('origin', moa_id, mob_id)
        self.swap_fields('sale_order_id', moa_id, mob_id)
        self.swap_fields('partner_id', moa_id, mob_id)
        self.swap_fields('date_planned_start', moa_id, mob_id)
        self.swap_fields('date_planned_finished', moa_id, mob_id)
        self.swap_fields('note', moa_id, mob_id)
        self.swap_fields(
            'project_id',
            moa_id.with_context(ignore_constrains_project_timesheets=True),
            mob_id.with_context(ignore_constrains_project_timesheets=True)
        )

        if swap_final_moves:
            self.swap_fields(
                'move_dest_ids', moa_id.move_finished_ids,
                mob_id.move_finished_ids
            )

        self.swap_production_request_content(
            moa_id.mrp_production_request_id, mob_id.mrp_production_request_id,
            swap_final_moves
        )

        self.update_timesheet_project(moa_id)
        self.update_timesheet_project(mob_id)

        self.message_post_swap(moa_id, mob_id)

    @api.model
    def update_timesheet_project(self, production_id):
        for al in production_id.timesheet_ids:
            if al.task_id:
                al.task_id.project_id = production_id.project_id
            al.project_id = production_id.project_id

    @api.model
    def swap_production_request_content(self, pra_id, prb_id, swap_final_moves):
        for field in self._get_fields_that_must_be_identical(
        )['mrp.production.request']:
            if pra_id[field] != pra_id[field]:
                raise Exception(_('%s must be the same') % (field))

        self.swap_fields('sale_order_id', pra_id, prb_id)
        self.swap_fields('partner_id', pra_id, prb_id)
        self.swap_fields('description', pra_id, prb_id)

        if swap_final_moves:
            self.swap_fields('origin', pra_id, prb_id)
            self.swap_fields('date_planned_start', pra_id, prb_id)
            self.swap_fields('date_planned_finished', pra_id, prb_id)

            # We choose to swap the `created_mrp_production_request_id`
            # instead of the `move_dest_ids` of the `production.request`
            pra_id_move = self.env['stock.move'].search(
                [('created_mrp_production_request_id', '=', pra_id.id)],
                limit=1
            )
            prb_id_move = self.env['stock.move'].search(
                [('created_mrp_production_request_id', '=', prb_id.id)],
                limit=1
            )
            self.swap_fields(
                'created_mrp_production_request_id', pra_id_move, prb_id_move
            )
        self.message_post_swap(pra_id, prb_id)

    def message_post_swap(self, obja_id, objb_id):
        def _get_link(obj_id):
            return '<a href="#" data-oe-model="%s" data-oe-id="%d">%s</a>' % (
                obj_id._name, obj_id.id, obj_id.name
            )

        message = _('🔄 Swapped with %s') % (_get_link(objb_id))
        obja_id.message_post(body=message)
        message = _('🔄 Swapped with %s') % (_get_link(obja_id))
        objb_id.message_post(body=message)

    def do_swap(self):
        self.ensure_one()
        for line in self.swap_line_ids:
            self.swap_production(
                line.from_production_id,
                line.to_production_id,
                line.swap_final_moves,
            )
