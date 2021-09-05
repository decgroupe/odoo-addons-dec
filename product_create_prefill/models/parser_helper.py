# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2020

import os
import sys
import random
import re
import json
import requests
import unicodedata
import importlib
import logging

from lxml import html
from collections import OrderedDict

# https://stackoverflow.com/questions/23705304/can-json-loads-ignore-trailing-commas
from jsoncomment import JsonComment

from . import requests_html

_logger = logging.getLogger(__name__)


def reload():
    importlib.reload(requests_html)


def dict_to_json(value):
    return str(json.dumps(
        value,
        indent=4,
        ensure_ascii=False,
    ))


def remove_nonvisible_unicodes(text):
    """ [summary]
        https://stackoverflow.com/questions/17978720/invisible-characters-ascii
    """
    CHARLIST = [
        # '\u2000',  #    En Quad                &#8192;      " "
        # '\u2001',  #    Em Quad                &#8193;      " "
        # '\u2002',  #    En Space               &#8194;      " "
        # '\u2003',  #    Em Space               &#8195;      " "
        # '\u2004',  #    Three-Per-Em Space     &#8196;      " "
        # '\u2005',  #    Four-Per-Em Space      &#8197;      " "
        # '\u2006',  #    Six-Per-Em Space       &#8198;      " "
        # '\u2007',  #    Figure Space           &#8199;      " "
        # '\u2008',  #    Punctuation Space      &#8200;      " "
        # '\u2009',  #    Thin Space             &#8201;      " "
        # '\u200a',  #    Hair Space             &#8202;      " "
        '\u200b',  #    Zero-Width Space       &#8203;      "​"
        '\u200c',  #    Zero Width Non-Joiner  &#8204;      "‌"
        '\u200d',  #    Zero Width Joiner      &#8205;      "‍"
        '\u200e',  #    Left-To-Right Mark     &#8206;      "‎"
        '\u200f',  #    Right-To-Left Mark     &#8207;      "‏"
        # '\u202f',  #    Narrow No-Break Space  &#8239;      " "
        # '\u2800',  #    Braille blank pattern  &#10240;     "⠀"
    ]
    for char in CHARLIST:
        text = text.replace(char, '')
    return text


def replace_unicode_spaces_with_standard_spaces(text):
    """ Replace all whitespace

        This includes all unicode whitespace, as described in the answer to
        this question: https://stackoverflow.com/questions/37903317/is-there-a-python-constant-for-unicode-whitespace
        From that answer, you can see that (at the time of writing), the
        unicode constants recognized as whitespace (e.g. \s) in Python
        regular expressions are these:

        0x0009
        0x000A
        0x000B
        0x000C
        0x000D
        0x001C
        0x001D
        0x001E
        0x001F
        0x0020
        0x0085
        0x00A0
        0x1680
        0x2000
        0x2001
        0x2002
        0x2003
        0x2004
        0x2005
        0x2006
        0x2007
        0x2008
        0x2009
        0x200A
        0x2028
        0x2029
        0x202F
        0x205F
        0x3000
    """
    _logger.info(text)
    return re.sub(r'\s', ' ', text)


def clean_text(text):
    text = replace_unicode_spaces_with_standard_spaces(text)
    text = remove_nonvisible_unicodes(text)
    return text


def fill_common_data(
    code,
    name,
    manufacturer,
    description,
    public_price,
    purchase_price,
    supplier,
    image_url,
    other={}
):
    res = {
        'code': clean_text(code),
        'name': clean_text(name),
        'manufacturer': clean_text(manufacturer),
        'description': clean_text(description),
        'public_price': public_price,
        'purchase_price': purchase_price,
        'supplier': clean_text(supplier),
        'image_url': clean_text(image_url),
        'other': other,
    }
    return res


# ua_version = random.randint(75, 78)
# user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{0}.0) Gecko/20100101 Firefox/{0}.0".format(
#     ua_version
# )

# HEADERS = {
#     "User-Agent": user_agent,
#     "Accept-Encoding": "gzip, deflate",
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#     "DNT": "1",
#     "Connection": "close",
#     "Upgrade-Insecure-Requests": "1",
# }

# Internet Explorer 11 on Windows 10
# Using https://www.whatismybrowser.com/detect/what-http-headers-is-my-browser-sending
HEADERS = {
    "ACCEPT":
        "text/html, application/xhtml+xml, image/jxr, */* ",
    "ACCEPT-ENCODING":
        "gzip, deflate",
    "ACCEPT-LANGUAGE":
        "fr-FR,fr;q=0.5 ",
    "USER-AGENT":
        "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"
}


def get_html_tree(content, use_javascript=False):
    if use_javascript:
        session = requests_html.HTMLSession()
        r = session.get(content)
        r.html.render()  # this call executes the js in the page
        content = r.html.html
    else:
        # Convert URL to HTML content
        if content.startswith('http'):
            page = requests.get(content, headers=HEADERS)
            #print(page.encoding)
            content = page.content.decode(page.encoding)
            #print(content)

        if 'captcha' in str(content):
            path = os.path.dirname(__file__)
            f = open(os.path.join(path, '_captcha_out.html'), 'w')
            f.write(content)
            f.close()
            print(
                'CAPTCHA REQUEST DETECTED, OUTPUT WRITTEN TO _captcha_out.html'
            )

    tree = html.fromstring(content)
    return tree


def normalize_caseless(text):
    return unicodedata.normalize("NFKD", text.casefold())


def caseless_equal(left, right):
    return normalize_caseless(left) == normalize_caseless(right)


def load_json_string(string, create_file=False, output_filename='./out.json'):
    if create_file:
        f = open(output_filename, 'w')
        f.write(string)
        f.close()
    res = JsonComment(json).loads(string, object_pairs_hook=OrderedDict)
    return res


def clean(xpath_res):
    if isinstance(xpath_res, list):
        if not xpath_res:
            return ''
        xpath_res = ' '.join(xpath_res)
    # We could use span[normalize-space(translate(text(),"\n", ""))
    xpath_res = os.linesep.join(
        [s for s in xpath_res.splitlines() if s.strip()]
    )
    xpath_res = xpath_res.strip()
    # Remove non-breaking space characters
    xpath_res = xpath_res.replace(u'\u00a0', '')
    # Remove multiple spaces
    xpath_res = re.sub(' +', ' ', xpath_res)
    return xpath_res


class ParserResultDict(OrderedDict):
    def __init__(self):
        super()
        self['description'] = ''

    def add_description_title(self, name):
        if name:
            if self['description']:
                self['description'] += os.linesep * 2
            self['description'] += '{}:'.format(name.rstrip(':'))

    def add_description(self, name, value, prefix='-'):
        if name and value:
            if self['description']:
                self['description'] += os.linesep
            self['description'] += '{} {}: {}'.format(
                prefix,
                name.rstrip(':'),
                value,
            )


reload()
