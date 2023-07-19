# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2020

import importlib

from . import parser_helper, parser_helper_prices


def reload():
    importlib.reload(parser_helper)
    importlib.reload(parser_helper_prices)


def parse(content):
    print("Parsing with", __name__)

    tree = parser_helper.get_html_tree(content, use_javascript=True)
    result = parser_helper.ParserResultDict()
    result["title"] = parser_helper.clean(
        tree.xpath('/html/head/meta[@property="og:title"]/@content')
    )
    result["description"] = parser_helper.clean(
        tree.xpath('/html/head/meta[@property="og:description"]/@content')
    )
    result["price"] = parser_helper.clean(
        tree.xpath(
            '//span[@itemprop="price" and contains(@class, "hideFromPro")]/@content'
        )
    )
    result["currency"] = parser_helper.clean(
        tree.xpath(
            '//span[@itemprop="price" and contains(@class, "hideFromPro")]/descendant-or-self::*/text()'
        )
    )
    result["brand"] = parser_helper.clean(
        tree.xpath('//span[@itemprop="brand"]/text()')
    )
    if not result["brand"]:
        result["marque"] = parser_helper.clean(
            tree.xpath(
                '//td[text()="Marque"]/following-sibling::node()/span/a/span/text()'
            )
        )

    result["id"] = parser_helper.clean(
        tree.xpath('//input[@name="TechnicalForm.ProductId"]/@value')
    )
    result["image"] = parser_helper.clean(
        tree.xpath('//div[@class="fpMainImg"]//a[@itemprop="image"]/@href')
    )

    if not result["image"]:
        result["image"] = parser_helper.clean(
            tree.xpath('/html/head/meta[@property="og:image"]/@content')
        )

    # Get technical description
    rows = tree.xpath('//table[@class="fpDescTb fpDescTbPub"]//tr')
    print(len(rows))
    for tr in rows:
        tds = tr.xpath("./td")
        # Keep only rows with at least two columns (remove titles)
        if len(tds) >= 2:
            name = tds[0].xpath("string(text())").strip()
            value = tds[1].xpath("string(text())").strip()
            result.add_description(name, value)

    result["seller"] = parser_helper.clean(
        tree.xpath('//a[@class="fpSellerName"]/text()')
    )

    seller = "CDiscount"
    if result["seller"]:
        seller = "{} ({})".format(seller, result["seller"])

    result["price_ttc"] = parser_helper_prices.to_float(
        result["price"] or "0", currency=result["currency"]
    )

    result = parser_helper.fill_common_data(
        code=result["id"] or "",
        name=result["title"] or "",
        manufacturer=result["brand"] or "",
        description=result["description"] or "",
        public_price=result["price_ttc"] / parser_helper_prices.TVA_20,
        purchase_price=result["price_ttc"] / parser_helper_prices.TVA_20,
        supplier=seller,
        image_url=result["image"] or "",
        other=result,
    )
    return result


reload()
