# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2020


def lf2html(text):
    """Replace \n and \r"""
    text = text.replace("\n", "<br/>")
    text = text.replace("\r", "<br/>")
    return text


def div(content, html_class=""):
    if html_class:
        return f'<div class="{html_class}">{content}</div>'
    else:
        return f"<div>{content}</div>"


def ul(content):
    return f"<ul>{content}</ul>"


def li(content):
    return f"<li>{content}</li>"


def small(content):
    return f"<small>{content}</small>"


def b(content):
    return f"<b>{content}</b>"


def p(content):
    return f"<p>{content}</p>"


def format_hd(head, desc, html):
    if html:
        return f"{head} {small(lf2html(desc))}"
    else:
        return f"{head} {desc}"
