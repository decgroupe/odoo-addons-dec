import logging

from openupgradelib import openupgrade
from odoo import SUPERUSER_ID, api, exceptions
from psycopg2.extensions import AsIs

_logger = logging.getLogger(__name__)


def migrate_bom_lines(env):
    cr = env.cr
    cr.execute(
        "ALTER TABLE ref_market_bom DROP CONSTRAINT ref_market_bom_bom_id_fkey"
    )
    created_from_bom_id = openupgrade.get_legacy_name('created_from_bom_id')
    cr.execute(
        "ALTER TABLE ref_market_bom_line ADD COLUMN %s INTEGER",
        (AsIs(created_from_bom_id), )
    )

    fields = {
        'product_uom_id': openupgrade.get_legacy_name('product_uom_id'),
        'product_qty': openupgrade.get_legacy_name('product_qty'),
        'bom_id': openupgrade.get_legacy_name('bom_id'),
        'partner_id': openupgrade.get_legacy_name('partner_id'),
        'locked_price': openupgrade.get_legacy_name('locked_price'),
        'price': openupgrade.get_legacy_name('price'),
    }
    sql = \
        """
        SELECT id, %(bom_id)s, product_id,
        %(product_uom_id)s, %(product_qty)s, %(partner_id)s, %(locked_price)s,
        %(price)s
        FROM ref_market_bom
        WHERE %(bom_id)s is NOT NULL
        """ % fields
    cr.execute(sql)
    REF_MARKET_BOM_LINE = env['ref.market.bom.line']
    ids = []
    for row in cr.dictfetchall():
        bom_line_id = REF_MARKET_BOM_LINE.sudo().create(
            {
                'market_bom_id': row[fields['bom_id']],
                'product_id': row['product_id'],
                'product_uom_id': row[fields['product_uom_id']],
                'product_qty': row[fields['product_qty']],
                'partner_id': row[fields['partner_id']],
                'locked_price': row[fields['locked_price']],
                'price': row[fields['price']],
            }
        )
        cr.execute(
            "UPDATE ref_market_bom_line SET %s = %s WHERE id = %s",
            (AsIs(created_from_bom_id), row['id'], bom_line_id.id)
        )
        ids.append(str(row['id']))

    if ids:
        openupgrade.logged_query(cr,
            "DELETE FROM ref_market_bom WHERE id in (%s)" % ','.join(ids)
        )


def migrate(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        migrate_bom_lines(env)
