import logging

from openupgradelib import openupgrade
from odoo import SUPERUSER_ID, api, exceptions
from psycopg2.extensions import AsIs

_logger = logging.getLogger(__name__)


def migrate_market_fields(env):
    cr = env.cr

    fields = {
        'market_bom_id':
            openupgrade.get_legacy_name('market_bom_id'),
        'market_markup_rate':
            openupgrade.get_legacy_name('market_markup_rate'),
        'market_material_cost_factor':
            openupgrade.get_legacy_name('market_material_cost_factor'),
    }
    sql = \
        """
        SELECT id, %(market_bom_id)s,
        %(market_markup_rate)s, %(market_material_cost_factor)s
        FROM product_template
        WHERE %(market_bom_id)s is NOT NULL
        """ % fields
    cr.execute(sql)
    REF_MARKET_BOM = env['ref.market.bom']
    ids = []
    for row in cr.dictfetchall():
        market_bom_id = REF_MARKET_BOM.sudo().search(
            [('product_tmpl_id', '=', row['id'])]
        )
        if market_bom_id:
            market_bom_id.write(
                {
                    'markup_rate':
                        row[fields['market_markup_rate']],
                    'material_cost_factor':
                        row[fields['market_material_cost_factor']],
                }
            )
        else:
            raise Exception("Market BoM not found")


def migrate(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        migrate_market_fields(env)
