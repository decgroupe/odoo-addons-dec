# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2020

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
    result['name'] = parser_helper.clean(
        tree.xpath(
            '//div[@class="titreDescription"]//span[@itemprop="name"]/text()'
        )
    )
    result['brand'] = parser_helper.clean(
        tree.xpath(
            '//div[@class="titreDescription"]//span[@itemprop="brand"]/descendant-or-self::*/text()'
        )
    )
    result['price'] = parser_helper.clean(
        tree.
        xpath('//div[@class="prices-block"]//meta[@itemprop="price"]/@content')
    )
    result['currency'] = parser_helper.clean(
        tree.xpath(
            '//div[@class="prices-block"]//meta[@itemprop="priceCurrency"]/@content'
        )
    )
    result['description_short'] = parser_helper.clean(
        tree.xpath('//*[@itemprop="description"]/text()')
    )

    result['images'] = []
    rows = tree.xpath(
        '//div[contains(@class, "imagesThumsDesktop")]//li[contains(@class, "thumb")]'
    )
    print(len(rows))
    for item in rows:
        url = parser_helper.clean(item.xpath('./a/@data-image'))
        result['images'].append(url)

    # Get technical description
    rows = tree.xpath(
        '//div[@data-target="fiche-technique"]//ul[@class="liste-attibutes"]//li'
    )
    print(len(rows))
    for item in rows:
        name = item.xpath(
            'string(./div[@class="spec-title"]/descendant-or-self::*/text())'
        ).strip()
        value = item.xpath(
            'string(./div[@class="spec"]/descendant-or-self::*/text())'
        ).strip()
        result.add_description(name, value)

    result['seller'] = parser_helper.clean(
        tree.xpath('//a[@class="sellerName"]/text()')
    )
    seller = 'Rue du Commerce'
    if result['seller'
             ] and not parser_helper.caseless_equal(seller, result['seller']):
        seller = '{} ({})'.format(seller, result['seller'])

    result['price_ttc'] = parser_helper_prices.to_float(
        result['price'] or '0', currency=result['currency']
    )

    result = parser_helper.fill_common_data(
        code=result['name'] or '',
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
