#!/usr/bin/python3

import os
import json
import requests
import binascii
import struct

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

def check_firmware(model):
    print("Checking firmware availability")
    print("------------------------------")

    ok = True
    releases = json.loads(open('firmware/' + str(model) +'/releases.json', 'r').read())

    # Find out the latest firmware release
    latest = [0, 0, 0]
    for r in releases:
        latest = max(latest, r['version'])

    print("Latest firmware: %s" % '.'.join(str(x) for x in latest))

    for r in releases:
        # Check only latest firmware, others may not be available yet
        if r['version'] != latest:
            continue

        firmware = r['url']
        version = '.'.join([ str(x) for x in r['version'] ])

        if version not in firmware:
            print("Missing '%s' in '%s'" % (version, firmware))
            ok = False
            continue

        print("Checking", firmware)
        if firmware.startswith('http'):
            ret = requests.get(firmware)
            if ret.status_code != 200:
                print("Missing firmware file", firmware)
                ok = False
                continue
            else:
                data = bytes(ret.text, 'utf-8')

        else:
            if not os.path.exists(firmware[len('data/'):]):
                print("Missing firmware file", firmware)
                ok = False
                continue
            else:
                data = open(firmware[len('data/'):], 'rb').read()

        start = b'TRZR' if model == 1 else b'TRZV'

        if not data.startswith(binascii.hexlify(start)):
            print("Corrupted file header:", firmware)
            ok = False
            continue

        if model == 1:
            codelen = struct.unpack('<I', binascii.unhexlify(data[8:16]))
            codelen = codelen[0]
            if codelen + 256 != len(data) // 2:
                print("Sanity check for firmware size failed (is %d bytes, should be %d bytes)" % (codelen + 256, len(data) // 2))
                ok = False
                continue

            if len(data) / 2 > 512*1024 - 32*1024: # Firmware - header - signatures
                print("File size is over limit:", firmware)
                ok = False
                continue

        if model == 2:
            vendorlen = struct.unpack('<I', binascii.unhexlify(data[8:16]))
            vendorlen = vendorlen[0]
            headerlen = struct.unpack('<I', binascii.unhexlify(data[8 + vendorlen*2:16 + vendorlen*2]))
            headerlen = headerlen[0]
            codelen = struct.unpack('<I', binascii.unhexlify(data[24 + vendorlen*2:32 + vendorlen*2]))
            codelen = codelen[0]

            if codelen + vendorlen + headerlen!= len(data) // 2:
                print("Sanity check for firmware size failed (is %d bytes, should be %d bytes)" % (codelen + vendorlen + headerlen, len(data) // 2))
                ok = False
                continue

    return ok

if __name__ == '__main__':
    ok = True
    ok &= check_bridge()
    ok &= check_firmware(1)
    ok &= check_firmware(2)

    if ok:
        print("EVERYTHING IS OK")
        exit(0)
    else:
        print("SOME PROBLEMS FOUND")
        exit(1)

