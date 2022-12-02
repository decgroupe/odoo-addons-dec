# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class PurchaseOrderMerge(models.TransientModel):
    _name = 'purchase.order.merge'
    _description = 'Merge Purchase Order'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Vendor',
    )
    order_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Purchase Order',
    )
    origin_order_ids = fields.Many2many(
        comodel_name='purchase.order',
        string='Origin Orders',
        readonly=True,
    )
    group_id = fields.Many2one(
        comodel_name='procurement.group',
        string="Procurement Group",
        help="Multiple orders means multiple procurement groups. You need to "
        "select which group will be used in the newly created order.",
    )
    pre_process = fields.Selection(
        selection=[
            ('create', 'Create new order'),
            ('merge', 'Merge orders on selected order'),
        ],
        string="Merge Mode",
        default='create'
    )
    post_process = fields.Selection(
        selection=[
            ('cancel', 'Cancel'),
            ('delete', 'Delete'),
        ],
        string="Remaining Order(s)",
        default='cancel'
    )
    merge_quantities = fields.Boolean(
        string='Merge Quantities',
        help="If checked, all lines with the same product will be merged "
        "and their quantities will be added",
    )

    def _check_selection_count(self, order_ids):
        if len(order_ids) < 2:
            raise UserError(
                _("Please select two or more orders in the list view")
            )

    def _check_selection_state(self, order_ids):
        PurchaseOrder = self.env['purchase.order']
        selection_states = order_ids.mapped('state')
        mergeable_states = PurchaseOrder._get_mergeable_states()
        diff_states = set(selection_states) - set(mergeable_states)
        if diff_states:
            display_states = {}
            # Get human readable incompatible state names
            for state in diff_states:
                display_state = dict(
                    PurchaseOrder._fields['state']._description_selection(
                        self.env
                    )
                ).get(state)
                display_states[state] = display_state
            invalid_po = []
            for order_id in order_ids.filtered(
                lambda p: p.state in diff_states
            ):
                invalid_po.append(
                    '{} state is {}'.format(
                        order_id.display_name, display_states[order_id.state]
                    )
                )

            raise UserError(
                _("Selection contains order(s) in incompatible states:\n%s") %
                ('\n - '.join([''] + invalid_po))
            )

    def _check_selection_partners(self, order_ids):
        partner_ids = order_ids.mapped('partner_id')
        if len(partner_ids) > 1:
            raise UserError(
                _(
                    "All orders must have the same supplier.\n"
                    "You have selected orders from these partners:\n%s"
                ) % ('\n - '.join([''] + partner_ids.mapped('display_name')))
            )

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')

        if active_model == 'purchase.order' and active_ids:
            origin_order_ids = self.env['purchase.order'].browse(active_ids)
            # Ensure selected data is valid
            self._check_selection_count(origin_order_ids)
            self._check_selection_state(origin_order_ids)
            self._check_selection_partners(origin_order_ids)
            # Assign wizard default values
            partner_id = origin_order_ids.mapped('partner_id')
            rec.update(
                {
                    'partner_id': partner_id.id,
                    'origin_order_ids': [(6, 0, origin_order_ids.ids)],
                }
            )
        return rec

    @api.onchange('order_id')
    def _onchange_order_id(self):
        self.group_id = self.order_id.group_id

    def _try_merging(self, line):
        match_line = False
        if self.order_id.order_line:
            for po_line in self.order_id.order_line:
                if line.product_id == po_line.product_id \
                and line.product_uom == po_line.product_uom \
                and line.price_unit == po_line.price_unit \
                and line.procurement_group_id == po_line.procurement_group_id \
                and line.taxes_id == po_line.taxes_id \
                and line.name == po_line.name:
                    match_line = po_line
                    break
        if match_line:
            match_line.product_qty += line.product_qty
            match_line.move_ids += line.move_ids
            match_line.move_dest_ids += line.move_dest_ids
            return True
        else:
            return False

    def _pre_process_create(self):
        self.order_id = self.env['purchase.order'].with_context(
            {
                'trigger_onchange': True,
                'onchange_fields_to_trigger': [self.partner_id]
            }
        ).create({
            'partner_id': self.partner_id.id,
            'date_order': min(self.origin_order_ids.mapped('date_order')),
        })
        self._pre_process_merge()

    def _pre_process_merge(self):
        # Remove selected order from list
        self.origin_order_ids -= self.order_id
        sequences = self.order_id.order_line.mapped('sequence')
        if sequences:
            sequence = max(sequences)
        else:
            sequence = 0
        for order in self.origin_order_ids:
            for line in order.order_line:
                if self.merge_quantities:
                    merged = self._try_merging(line)
                    line.unlink()
                else:
                    merged = False
                if not merged:
                    sequence += 1
                    line.write(
                        {
                            'sequence': sequence,
                            'order_id': self.order_id.id,
                        }
                    )
        self._set_origin()
        self.order_id.message_post_with_view(
            'purchase_merge.merged_with_template',
            values={
                'order_ids': self.origin_order_ids,
            },
            subtype_id=self.env.ref('mail.mt_note').id,
        )

    def _set_origin(self):
        if self.order_id.origin:
            self.order_id.origin += ','
        else:
            self.order_id.origin = ''
        display_names = list(set(self.origin_order_ids.mapped('display_name')))
        self.order_id.origin += ','.join(display_names)

    def _post_process_cancel(self):
        for order_id in self.origin_order_ids:
            order_id.message_post_with_view(
                'purchase_merge.merged_to_template',
                values={
                    'order_id': self.order_id,
                },
                subtype_id=self.env.ref('mail.mt_note').id,
            )
            order_id.button_cancel()

    def _post_process_delete(self):
        self.post_process_cancel()
        for order_id in self.origin_order_ids:
            order_id.sudo().unlink()

    def action_merge(self):
        if self.pre_process == 'create':
            self._pre_process_create()
        elif self.pre_process == 'merge':
            self._pre_process_merge()

        if self.post_process == 'cancel':
            self._post_process_cancel()
        elif self.post_process == 'delete':
            self._post_process_delete()

        action_vals = {
            'name': _('Purchase Orders (after merge)'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.order_id.id,
            'res_model': 'purchase.order',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        return action_vals
