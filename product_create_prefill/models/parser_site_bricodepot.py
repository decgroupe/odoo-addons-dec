# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jun 2020

import importlib

from urllib.parse import urlparse
from pprint import pformat

from . import parser_helper
from . import parser_helper_prices


def reload():
    importlib.reload(parser_helper)
    importlib.reload(parser_helper_prices)


def parse(content):
    print("Parsing with", __name__)

    hostname = urlparse(content).hostname
    tree = parser_helper.get_html_tree(content)
    result = parser_helper.ParserResultDict()

    result['name'] = parser_helper.clean(
        tree.xpath(
            '//h1[@class="bd-ProductCard-title"]/span[@itemprop="name"]/text()'
        )
    )

    raw_json_data = tree.xpath(
        '//section[@id="bd-Anchor-desc"]/@data-product-infos'
    )
    data = parser_helper.load_json_string(parser_helper.clean(raw_json_data))

    result['brand'] = data.get('brand')
    result['code'] = data.get('skuId')
    result['price'] = data.get('price')

    result['currency'] = parser_helper.clean(
        tree.xpath(
            '//div[@class="bd-ProductCard-InfoBox"]//meta[@itemprop="priceCurrency"]/@content'
        )
    )

    result['images'] = []
    pictures = tree.xpath(
        '//li[contains(@class, "bd-ProductView-item")]/picture/img'
    )
    print(len(pictures))
    for p in pictures:
        result['images'].append(hostname + parser_helper.clean(p.xpath('./@data-src')))

    # Get technical description
    nodes = tree.xpath('//p[@class="bd-ProductDetails-tableTitle"]')
    for node in nodes:
        name = parser_helper.clean(node.xpath('string(./text())'))
        value = False
        next_nodes = node.xpath('./following-sibling::*')
        if next_nodes:
            next_node = next_nodes[0]
            if next_node.tag == 'p' and 'bd-ProductDetails-tableDesc' in next_node.get(
                'class'
            ):
                value = parser_helper.clean(next_node.xpath('string(./text())'))
                result.add_description(name, value)
            if next_node.tag == 'ul':
                lis = next_node.xpath('.//li')
                result.add_description_title(name)
                for li in lis:
                    name = parser_helper.clean(
                        li.xpath(
                            'string(./div[@class="bd-ProductDetails-index"]/text())'
                        )
                    )
                    value = parser_helper.clean(
                        li.xpath(
                            'string(./div[@class="bd-ProductDetails-val"]/text())'
                        )
                    )
                    result.add_description(name, value, '  -')

    result['price_ttc'] = parser_helper_prices.to_float(
        result['price'] or '0', currency=result['currency']
    )

    seller = 'Brico Depot'

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
    print(pformat(result))
    return result

reload()
