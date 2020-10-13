#!/usr/bin/python

import sys
import argparse
from gnupg import GPG

parser = argparse.ArgumentParser()
parser.add_argument('--pass')
parser.add_argument('files', nargs='*')
p = vars(parser.parse_args(sys.argv[1:]))
passphrase = p['pass']
inputfiles = p.get('files')
gpg = GPG()

if len(gpg.list_keys(False)) == 0:
    print("No keys found. Do you need to enter a virtual environment?")
    exit(1)

def decrypt(input):
    try:
        lines = []
        for line in input:
            if len(line):
                lines.append(line)
                if line == '-----END PGP MESSAGE-----\n':
                    message = ''.join(lines)
                    d = gpg.decrypt(message, always_trust=True)
                    print(d or "Couldn't decrypt message")
                    lines.clear()
    finally:
        pass

if len(inputfiles):
    for inputfile in inputfiles:
        print("\n%s:" % inputfile)
        input = open(inputfile, 'r')
        decrypt(input)
        input.close()
else:
    decrypt(sys.stdin)
