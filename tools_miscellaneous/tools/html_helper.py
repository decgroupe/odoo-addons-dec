# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2020

from odoo.tools import plaintext2html


def lf2html(text):
    """ Replace \n and \r """
    text = text.replace('\n', '<br/>')
    text = text.replace('\r', '<br/>')
    return text


def div(content, html_class=''):
    if html_class:
        return '<div class="{}">{}</div>'.format(html_class, content)
    else:
        return '<div>{}</div>'.format(content)


def ul(content):
    return '<ul>{}</ul>'.format(content)


def li(content):
    return '<li>{}</li>'.format(content)


def small(content):
    return '<small>{}</small>'.format(content)


def b(content):
    return '<b>{}</b>'.format(content)


def format_hd(head, desc, html):
    if html:
        return '{0} {1}'.format(head, small(lf2html(desc)))
    else:
        return '{0} {1}'.format(head, desc)
