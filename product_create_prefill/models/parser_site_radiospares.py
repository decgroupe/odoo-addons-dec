# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jun 2020

import importlib

from . import parser_helper
from . import parser_helper_prices


def reload():
    importlib.reload(parser_helper)
    importlib.reload(parser_helper_prices)


def parse(content):
    print("Parsing with", __name__)

    tree = parser_helper.get_html_tree(content)
    result = parser_helper.ParserResultDict()

    jsons = tree.xpath('//script[@type="application/ld+json"]/text()')
    for item in jsons:
        data = parser_helper.load_json_string(item)
        if data.get('@type') == 'Product':
            print(pformat(data))
            result['name'] = data.get('name')
            result['code'] = data.get('sku')
            result['images'] = data.get('image')
            result['description_short'] = data.get('description')
            brand = data.get('brand')
            if brand:
                result['brand'] = brand.get('name')
            offers = data.get('offers')
            if offers:
                result['price'] = offers.get('price')
                result['currency'] = offers.get('priceCurrency')
        if data.get('@type') == 'BreadcrumbList':
            print(pformat(data))

    seller = 'RS COMPONENTS SAS'
    if result.get('seller'):
        seller = '{} ({})'.format(seller, result['seller'])

    # Get technical description
    rows = tree.xpath('(//div[@class="specifications"])[1]//table//tr')
    print(len(rows))
    for tr in rows:
        tds = tr.xpath("./td")
        if len(tds) >= 2:
            name = tds[0].xpath('string(text())').strip()
            value = tds[1].xpath('string(text())').strip()
            result.add_description(name, value)

    result['price_ttc'] = parser_helper_prices.to_float(result['price'] or '0')

    result = parser_helper.fill_common_data(
        code=result['code'] or '',
        name=result['name'] or '',
        manufacturer=result['brand'] or '',
        description=result['description'] or '',
        public_price=result['price_ttc'],
        purchase_price=result['price_ttc'] / parser_helper_prices.TVA_20,
        supplier=seller,
        image_url=result['images'] or '',
        other=result,
    )

    return result


reload()
