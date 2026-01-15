# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2023

# https://stackoverflow.com/a/42449998

RESET_SEQ = "\033[0m"
FORMAT_SEQ = "\033[%dm"

_NORMAL = 0
_BOLD = 1
_DIM = 2
_ITALIC = 3
_UNDERLINED = 4
_BLINKING = 5
_REVERSE = 7
_INVISIBLE = 8
_STRIKETHROUGH = 9

_FG_BLACK = 30
_FG_RED = 31
_FG_GREEN = 32
_FG_YELLOW = 33
_FG_BLUE = 34
_FG_MAGENTA = 35
_FG_CYAN = 36
_FG_WHITE = 37


def bold(text):
    return FORMAT_SEQ % (_BOLD) + text + RESET_SEQ


def dim(text):
    return FORMAT_SEQ % (_DIM) + text + RESET_SEQ


def italic(text):
    return FORMAT_SEQ % (_ITALIC) + text + RESET_SEQ


def underlined(text):
    return FORMAT_SEQ % (_UNDERLINED) + text + RESET_SEQ


def blinking(text):
    return FORMAT_SEQ % (_BLINKING) + text + RESET_SEQ


def reverse(text):
    return FORMAT_SEQ % (_REVERSE) + text + RESET_SEQ


def invisible(text):
    return FORMAT_SEQ % (_INVISIBLE) + text + RESET_SEQ


def strikethrough(text):
    return FORMAT_SEQ % (_STRIKETHROUGH) + text + RESET_SEQ

def black(text):
    return FORMAT_SEQ % (_FG_BLACK) + text + RESET_SEQ

def red(text):
    return FORMAT_SEQ % (_FG_RED) + text + RESET_SEQ


def green(text):
    return FORMAT_SEQ % (_FG_GREEN) + text + RESET_SEQ


def yellow(text):
    return FORMAT_SEQ % (_FG_YELLOW) + text + RESET_SEQ


def blue(text):
    return FORMAT_SEQ % (_FG_BLUE) + text + RESET_SEQ


def magenta(text):
    return FORMAT_SEQ % (_FG_MAGENTA) + text + RESET_SEQ


def cyan(text):
    return FORMAT_SEQ % (_FG_CYAN) + text + RESET_SEQ


def white(text):
    return FORMAT_SEQ % (_FG_WHITE) + text + RESET_SEQ
