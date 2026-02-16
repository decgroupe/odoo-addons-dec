# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2021

from ctypes import c_uint32


def encipher(v, k):
    y = c_uint32(v[0])
    z = c_uint32(v[1])
    som = c_uint32(0)
    delta = 0x9E3779B9
    n = 32
    w = [0, 0]

    while n > 0:
        som.value += delta
        y.value += (z.value << 4) + k[0] ^ z.value + som.value ^ (z.value >> 5) + k[1]
        z.value += (y.value << 4) + k[2] ^ y.value + som.value ^ (y.value >> 5) + k[3]
        n -= 1

    w[0] = y.value
    w[1] = z.value
    return w


def decipher(v, k):
    y = c_uint32(v[0])
    z = c_uint32(v[1])
    som = c_uint32(0xC6EF3720)
    delta = 0x9E3779B9
    n = 32
    w = [0, 0]

    while n > 0:
        z.value -= (y.value << 4) + k[2] ^ y.value + som.value ^ (y.value >> 5) + k[3]
        y.value -= (z.value << 4) + k[0] ^ z.value + som.value ^ (z.value >> 5) + k[1]
        som.value -= delta
        n -= 1

    w[0] = y.value
    w[1] = z.value
    return w
