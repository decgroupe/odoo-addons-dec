# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jun 2020

import importlib

from pprint import pformat

from . import parser_helper
from . import parser_helper_prices


def reload():
    importlib.reload(parser_helper)
    importlib.reload(parser_helper_prices)


def parse(content):
    print("Parsing with", __name__)

    tree = parser_helper.get_html_tree(content)
    result = parser_helper.ParserResultDict()

    result['title'] = parser_helper.clean(
        tree.xpath('//span[@id="productTitle"]/text()[normalize-space()]')
    )
    result['price_deal'] = parser_helper.clean(
        tree.xpath('//span[@id="priceblock_dealprice"]/text()')
    )
    result['price_our'] = parser_helper.clean(
        tree.xpath('//span[@id="priceblock_ourprice"]/text()')
    )
    result['price_sale'] = parser_helper.clean(
        tree.xpath('//span[@id="priceblock_saleprice"]/text()')
    )
    result['price_strike'] = parser_helper.clean(
        tree.
        xpath('//span[contains(@class, "priceBlockStrikePriceString")]/text()')
    )

    ## MODEL
    result['model'] = parser_helper.clean(
        tree.xpath(
            '//table//tr[@class="item-model-number"]//td[@class="value"]/text()'
        )
    )
    if not result['model']:
        result['model'] = parser_helper.clean(
            tree.xpath(
                '//table//th[contains(@class, "prodDetSectionEntry") and contains(text(),"Référence")]/following-sibling::node()/text()'
            )
        )

    ## MARQUE
    result['marque'] = parser_helper.clean(
        tree.xpath(
            '//td[@class="label" and text()="Marque"]/following-sibling::node()/text()'
        )
    )
    if not result['marque']:
        result['marque'] = parser_helper.clean(
            tree.xpath(
                '//table//th[contains(@class, "prodDetSectionEntry") and (contains(text(),"Marque") or contains(text(),"Fabricant"))]/following-sibling::node()/text()'
            )
        )

    ## ASIN
    result['asin'] = parser_helper.clean(
        tree.xpath(
            '//td[@class="label" and contains(text(),"ASIN")]/following-sibling::node()/text()'
        )
    )
    if not result['asin']:
        result['asin'] = parser_helper.clean(
            tree.xpath(
                '//table//th[contains(@class, "prodDetSectionEntry") and contains(text(),"ASIN")]/following-sibling::node()/text()'
            )
        )

    ## SELLER
    result['seller'] = parser_helper.clean(
        tree.xpath('//a[@id="sellerProfileTriggerId"]/text()')
    )
    ## IMAGES
    result['images'] = parser_helper.clean(
        tree.xpath('//img[@id="landingImage"]/@data-a-dynamic-image')
    )
    if result['images']:
        result['images'] = parser_helper.load_json_string(result['images'])

    # Get technical description
    rows = tree.xpath('(//div[@class="section techD"])[1]//table//tr')
    print(len(rows))
    if not rows:
        rows = tree.xpath(
            '(//table[@id="productDetails_techSpec_section_1"])[1]//tr'
        )
        print(len(rows))

    for tr in rows:
        name = False
        value = False
        ths = tr.xpath("./th")
        tds = tr.xpath("./td")
        # Table struct since Septembre 2020
        if len(ths) == 1 and len(tds) == 1:
            name = ths[0].xpath('string(text())').strip()
            value = tds[0].xpath('string(text())').strip()
        # Table struct before Septembre 2020
        if len(tds) >= 2:
            name = tds[0].xpath('string(text())').strip()
            value = tds[1].xpath('string(text())').strip()
        if name and value:
            result.add_description(name, value)

    seller = 'Amazon'
    if result['seller']:
        seller = '{} ({})'.format(seller, result['seller'])

    image = ''
    if result['images']:
        # Use next/iter to optimize
        first_image = next(iter(result['images'].items()))
        # Store key as image since URL is the key
        image = first_image[0]

    # Format data to common values
    result = parser_helper.fill_common_data(
        code=result['model'] or result['asin'],
        name=result['title'] or '',
        manufacturer=result['marque'] or result['seller'] or '',
        description=result['description'] or '',
        public_price=parser_helper_prices.to_float(
            result['price_strike'] or result['price_our'] or '0'
        ) / parser_helper_prices.TVA_20,
        purchase_price=parser_helper_prices.to_float(
            result['price_deal'] or result['price_sale'] or
            result['price_our'] or '0'
        ) / parser_helper_prices.TVA_20,
        supplier=seller,
        image_url=image,
        other=result,
    )
    print(pformat(result))
    return result


reload()
