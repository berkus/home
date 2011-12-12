# -*- coding: utf-8 -*-

''' My OpenSSL wrapper for dummy SSL certificates '''

from sys import argv, exit
from os.path import exists
from subprocess import call

# bare minimum conf required to keep 'openssl req' happy.
OPENSSL_CONF = '''[req]
distinguished_name=req_dn
[req_dn]'''

ROOT_FILES = ['root.crt', 'root.cnf', 'root.key']

COMMANDS = {
    'root-key-pair': ['openssl req -x509 -keyout root.pem -out root.crt -config root.cnf',
                      '-newkey rsa:1024 -days 365 -passout pass:badpass',
                      '-subj "/O=A1DRIN.NET/OU=DEVELOPMENT-ONLY/CN=Root CA for A1DRIN.NET"'],
    'user-key-pair': ['openssl req -new -keyout {0}.pem -out {0}.csr -config root.cnf',
                      '-newkey rsa:1024 -passout pass:badpass',
                      '-subj "/O=A1DRIN.NET/OU=DEVELOPMENT-ONLY/CN={0}"'],
    'strip-keypass': ['openssl rsa -in {0}.pem -out {0}.key -passin pass:badpass'],
    'sign-user-crt': ['openssl x509 -req -in {0}.csr -CA root.crt -CAkey root.key -days 365',
                      '-CAcreateserial -out {0}.crt'],
    }


def commandline():
    command = cn = None
    if len(argv) > 1:
        command = argv[1]
    if len(argv) > 2:
        cn = argv[2]

    if command == 'gen':
        if not reduce(lambda x, y: x and exists(y), ROOT_FILES, True):
            usage('root keys uninitialized (do <init> first.)')
        if not cn:
            usage('common-name is required with <gen>.')
    elif command == 'init':
        if reduce(lambda x, y: x or exists(y), ROOT_FILES, False):
            usage('root keys already initialized ("rm root.*" first.)')
    else:
        usage('%s <init|gen> [common-name]' % argv[0])
    return (command, cn)


def usage(message):
    print message
    exit(2)


def do(command, cn):
    if command == 'init':
        cnf = open('root.cnf', 'w')
        cnf.write(OPENSSL_CONF)
        cnf.close()
        root_key_pair = ' '.join(COMMANDS['root-key-pair'])
        strip_keypass = ' '.join(COMMANDS['strip-keypass']).format('root')
        return call(root_key_pair) == 0 and call(strip_keypass) == 0
    if command == 'gen':
        user_key_pair = ' '.join(COMMANDS['user-key-pair']).format(cn)
        strip_keypass = ' '.join(COMMANDS['strip-keypass']).format(cn)
        sign_user_crt = ' '.join(COMMANDS['sign-user-crt']).format(cn)
        return call(user_key_pair) == 0 and call(strip_keypass) == 0 and call(sign_user_crt) == 0
    return None


if __name__ == '__main__':
    if not do(*commandline()):
        print 'Fail'
