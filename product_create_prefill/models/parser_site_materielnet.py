# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2020

import importlib

from . import parser_helper
from . import parser_helper_prices
from . import parser_site_ldlc


def reload():
    importlib.reload(parser_helper)
    importlib.reload(parser_helper_prices)
    importlib.reload(parser_site_ldlc)


def parse(content):
    print("Parsing with", __name__)
    tree = parser_helper.get_html_tree(content)

    result = parser_site_ldlc._parse_group(tree)
    seller = 'Materiel.net'

    # Override short description
    result['description_short'] = parser_helper.clean(
        tree.
        xpath('//span[@class="c-product__specs"]/descendant-or-self::*/text()')
    )

    # Get technical description
    rows = tree.xpath('//table[contains(@class, "c-specs__table")]//tr')
    print(len(rows))
    for tr in rows:
        name = parser_helper.clean(
            tr.
            xpath('string(./td[@class="label"]/descendant-or-self::*/text())')
        )
        value = parser_helper.clean(
            tr.
            xpath('string(./td[@class="value"]/descendant-or-self::*/text())')
        )
        result.add_description(name, value)

    result = parser_helper.fill_common_data(
        code=result['code'] or '',
        name=result['name'] or '',
        manufacturer=result['brand'] or '',
        description=result['description'] or '',
        public_price=result['price_ttc'] / parser_helper_prices.TVA_20,
        purchase_price=result['price_ttc'] / parser_helper_prices.TVA_20,
        supplier=seller,
        image_url=result['images'] and result['images'][0] or '',
        other=result,
    )
    return result


reload()
