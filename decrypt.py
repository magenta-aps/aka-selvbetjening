#!/usr/bin/python

import os
import sys
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--pass')
parser.add_argument('files', nargs='*')
p = vars(parser.parse_args(sys.argv[1:]))
passphrase = p['pass']
inputfiles = p.get('files')

def decrypt(input):
    try:
        lines = []
        for line in input:
            if len(line):
                lines.append(line)
                if line == '-----END PGP MESSAGE-----\n':
                    message = ''.join(lines)
                    subprocess.run(["/usr/bin/gpg", "-d"], input=bytes(message, 'utf-8'))
                    lines.clear()
    finally:
        pass

def mkdir(folder):
    try:
        os.mkdir(folder)
    except FileExistsError:
        pass

if len(inputfiles):
    for inputfile in inputfiles:
        print("\n%s:" % inputfile)
        input = open(inputfile, 'r')
        decrypt(input)
        input.close()
else:
    decrypt(sys.stdin)

