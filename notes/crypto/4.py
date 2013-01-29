# -*- coding: utf-8 -*-

import binascii
import urllib2
import sys

TARGET = 'http://crypto-class.appspot.com/po?er='


# --------------------------------------------------------------
# padding oracle
# --------------------------------------------------------------

class PaddingOracle(object):

    def __init__(self):
        self.cache = {}

    def query(self, q):

        if q in self.cache:
            return self.cache[q]

        target = TARGET + urllib2.quote(q)  # Create query URL
        req = urllib2.Request(target)  # Send HTTP request to server
        try:
            f = urllib2.urlopen(req)  # Wait for response
        except urllib2.HTTPError, e:
            # print 'We got: %d' % e.code  # Print response code
            if e.code == 404:
                self.cache[q] = True
                return True  # good padding
            self.cache[q] = False
            return False  # bad padding


ctext = \
    'f20bdba6ff29eed7b046d1df9fb7000058b1ffb4210a580f748b4ac714c001bd4a61044426fb515dad3f21f18aa577c0bdf302936266926ff37dbf7035d5eeb4'
cipher = [ord(x) for x in binascii.unhexlify(ctext)]


def tohex(c):
    return ''.join(['%0.2x' % x for x in c])


def discover(po, cipher, suffix):
    m = ''
    pad = 0
    c = cipher[:]
    print tohex(c), tohex(suffix)
    for byte in range(15, -1, -1):
        pad += 1
        print tohex(c)
        print 'byte={0},pad={1}'.format(byte, pad)
        # pad the bytes with the new pad first
        for i in range(byte, 16):
            c[i] = c[i] ^ pad
        # for the current byte, try all values
        for g in range(0, 256):
            print g,
            sys.stdout.flush()
            c[byte] = c[byte] ^ g
            if po.query('f20bdba6ff29eed7b046d1df9fb7000058b1ffb4210a580f748b4ac714c001bd'
                        + tohex(c) + tohex(suffix)) or byte == 7 and g == 9:
                m = chr(g) + m
                print '{0}:\'{1}\''.format(g, m)
                # clear the pad
                for i in range(byte, 16):
                    c[i] = c[i] ^ pad
                break
            # clear this guess
            c[byte] = c[byte] ^ g


if __name__ == '__main__':
    po = PaddingOracle()
    discover(po, cipher[32:48], cipher[48:64])
