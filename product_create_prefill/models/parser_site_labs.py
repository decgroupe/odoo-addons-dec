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

    result = {}
    result['title'] = tree.xpath(
        '//span[@id="ctl00_MainPanel_FormViewArticle_LabelDescription"]/text()'
    )
    result['price_1'] = tree.xpath(
        '//span[@id="ctl00_MainPanel_FormViewArticle_MultiplePriceControl1_LabelPrice1"]/text()'
    )
    result['model'] = tree.xpath(
        '//span[@id="ctl00_MainPanel_FormViewArticle_LabelCodeArticle"]/text()'
    )
    result['marque'] = tree.xpath(
        '//img[@id="ctl00_MainPanel_FormViewArticle_imgMarque"]/@title'
    )

    return result


reload()
