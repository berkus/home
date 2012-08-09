#!/usr/bin/env python
# -*- coding: utf-8 -*-

COUNT = '1'
DATA = '100M'
PORT = '8443'
CIPHERS = 'TLSv1+aRSA'
SERVER = 'localhost'
AB = '/home/aldrin/pkg/apache/bin/ab'
OPENSSL = '/home/aldrin/pkg/openssl/bin/openssl'
URL = 'https://{0}:{1}/{2}'.format(SERVER, PORT, DATA)


def measure_cipher_rate():
    """ Runs the Apache HTTP benchmark tools iteratively over the a subset of ciphers and prints
    their transfer rates."""

    from subprocess import check_output
    from operator import itemgetter
    rates = {}
    openssl_cmd = '{0} ciphers -v {1}'.format(OPENSSL, CIPHERS)
    openssl_out = check_output(openssl_cmd.split())
    ciphers = [c.split()[0] for c in openssl_out.split('\n') if len(c) > 0]
    for cipher in ciphers:
        try:
            ab_cmd = '{0} -f tls1 -n {1} -Z {2} {3}'.format(AB, COUNT, cipher, URL)
            ab_out = check_output(ab_cmd.split(), stderr=file('/dev/null'))
            rate_line = [l for l in ab_out.split('\n') if l.startswith('Transfer rate:')][0]
            rates[cipher] = float(rate_line.split(':')[1].split('[')[0].strip())
        except:
            print 'unsupported cipher:', cipher
    for (k, v) in sorted(rates.iteritems(), key=itemgetter(1)):
        print '{0:<30} {1}'.format(k, v)


if __name__ == '__main__':
    measure_cipher_rate()
