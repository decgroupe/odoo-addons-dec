# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2020

import importlib

from . import parser_helper
from . import parser_helper_prices


def reload():
    importlib.reload(parser_helper)
    importlib.reload(parser_helper_prices)


def _parse_group(tree):

    result = parser_helper.ParserResultDict()
    jsons = tree.xpath('//script[@type="application/ld+json"]/text()')

    for item in jsons:
        data = parser_helper.load_json_string(item)
        if data.get('@type') == 'Product':
            result['name'] = data.get('name')
            result['code'] = data.get('mpn')
            result['images'] = data.get('image')
            result['description_short'] = data.get('description')
            brand = data.get('brand')
            if brand:
                result['brand'] = brand.get('name')
            offers = data.get('offers')
            if offers:
                result['price'] = offers.get('price')
                result['currency'] = offers.get('priceCurrency')

    # Get technical description
    rows = tree.xpath('//table[@id="product-parameters"]//tr')
    print(len(rows))
    for tr in rows:
        name = parser_helper.clean(
            tr.
            xpath('string(./td[@class="label"]/descendant-or-self::*/text())')
        )
        value = parser_helper.clean(
            tr.xpath(
                'string(./td[@class="checkbox"]/descendant-or-self::*/text())'
            )
        )
        if not value:
            value = parser_helper.clean(
                tr.xpath(
                    'string(./td[@class="checkbox"]//a/descendant-or-self::*/text())'
                )
            )
        result.add_description(name, value)

    result['price_ttc'] = parser_helper_prices.to_float(
        result['price'] or '0', currency=result['currency']
    )

    return result


def parse(content):
    print("Parsing with", __name__)

    tree = parser_helper.get_html_tree(content)

    result = _parse_group(tree)
    seller = 'LDLC.pro'

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
