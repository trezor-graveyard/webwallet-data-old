#!/usr/bin/python3

import os
import json
import requests
import binascii

def check_bridge():
    patterns = ['trezor-bridge-%(version)s-1.i386.rpm',
                'trezor-bridge-%(version)s-1.x86_64.rpm',
                'trezor-bridge-%(version)s-win32-install.exe',
                'trezor-bridge-%(version)s.pkg',
                'trezor-bridge_%(version)s_amd64.deb',
                'trezor-bridge_%(version)s_i386.deb']

    v = open('bridge/latest.txt', 'r').read().strip()
    print("Expected latest bridge version: %s" % v)

    if not os.path.isdir(os.path.join('bridge', v)):
        return False

    print("Checking files for bridge version", v)
    print("----------------------------------------")
    for p in patterns:
        expected = p % {'version': v}
        print(expected)
        if not os.path.isfile(os.path.join('bridge', v, expected)):
            print("Missing file %s/%s" % (v, expected))

    return ok

def check_firmware():
    print("Checking firmware availability")
    print("------------------------------")

    ok = True
    releases = json.loads(open('firmware/releases.json', 'r').read())
    for r in releases:
        firmware = r['url']
        version = '.'.join([ str(x) for x in r['version'] ])

        if version not in firmware:
            print("Missing '%s' in '%s'" % (version, firmware))
            ok = False

        print("Checking", firmware)
        if firmware.startswith('http'):
            ret = requests.get(firmware)
            if ret.status_code != 200:
                print("Missing firmware file", firmware)
                ok = False
                data = b''
            else:
                data = bytes(ret.text, 'utf-8')

        else:
            if not os.path.exists(firmware[len('data/'):]):
                print("Missing firmware file", firmware)
                ok = False
                data = b''
            else:
                data = open(firmware[len('data/'):], 'rb').read()

        if not data.startswith(binascii.hexlify(b'TRZR')):
            print("Corrupted file header:", firmware)
            ok = False

        if len(data) / 2 > 512*1024 - 32*1024: # Firmware - header - signatures
            print("File size is over limit:", firmware)
            ok = False

    return ok

if __name__ == '__main__':
    ok = True
    ok &= check_bridge()
    ok &= check_firmware()

    if ok:
        print("EVERYTHING IS OK")
        exit(0)
    else:
        print("SOME PROBLEMS FOUND")
        exit(1)

