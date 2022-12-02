# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

import importlib

from pprint import pformat

from . import parser_helper_prices
from . import parser_helper

from . import parser_site_amazon
from . import parser_site_cdiscount
from . import parser_site_topachat
from . import parser_site_rueducommerce
from . import parser_site_hardwarefr
from . import parser_site_materielnet
from . import parser_site_ldlc
from . import parser_site_labs
from . import parser_site_bricodepot
from . import parser_site_manomano
from . import parser_site_radiospares

def reload():
    importlib.reload(parser_helper_prices)
    importlib.reload(parser_site_amazon)
    importlib.reload(parser_site_cdiscount)
    importlib.reload(parser_site_topachat)
    importlib.reload(parser_site_rueducommerce)
    importlib.reload(parser_site_hardwarefr)
    importlib.reload(parser_site_materielnet)
    importlib.reload(parser_site_ldlc)
    importlib.reload(parser_site_labs)
    importlib.reload(parser_site_bricodepot)
    importlib.reload(parser_site_manomano)
    importlib.reload(parser_site_radiospares)


def parse_html_product_page(url):
    print(url)
    if 'amazon' in url:
        res = parser_site_amazon.parse(url)
    elif 'cdiscount' in url:
        res = parser_site_cdiscount.parse(url)
    elif 'rueducommerce' in url:
        res = parser_site_rueducommerce.parse(url)
    elif 'topachat' in url:
        res = parser_site_topachat.parse(url)
    elif 'materiel.net' in url:
        res = parser_site_materielnet.parse(url)
    elif 'ldlc' in url:
        res = parser_site_ldlc.parse(url)
    elif 'hardware.fr' in url:
        res = parser_site_hardwarefr.parse(url)
    elif 'bricodepot' in url:
        res = parser_site_bricodepot.parse(url)
    elif 'manomano' in url:
        res = parser_site_manomano.parse(url)
    elif 'rs-online' in url:
        res = parser_site_radiospares.parse(url)
    else:
        res = parser_helper.fill_common_data(
            code='?',
            name='?',
            manufacturer='',
            description='',
            public_price=0,
            purchase_price=0,
            supplier='',
            image_url='',
            other={},
        )

    print(pformat(res))
    return parser_helper.dict_to_json(res)


reload()
