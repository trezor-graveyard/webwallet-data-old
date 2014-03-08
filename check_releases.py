#!/usr/bin/python

import os
import json

def check_plugin():
    patterns = ['browser-plugin-trezor-%(version)s.i386.rpm',
                'browser-plugin-trezor-%(version)s.x86_64.rpm',
                'BitcoinTrezorPlugin-%(version)s.msi',
                'browser-plugin-trezor_%(version)s_i386.deb',
                'browser-plugin-trezor_%(version)s_amd64.deb']

    versions = os.listdir('plugin')
    versions.sort()

    ok = True
    latest = None
    for v in versions:
        if not os.path.isdir(os.path.join('plugin', v)):
            continue

        latest = v
        print "Checking files for version", v
        print "---------------------------------"

        for p in patterns:
            expected = p % {'version': v}
            if not os.path.isfile(os.path.join('plugin', v, expected)):
                ok = False
                print "Missing file %s/%s" % (v, expected)

    print "Checking latest.txt"
    print "-------------------"

    latest_file = open('plugin/latest.txt', 'r').read().strip()
    if latest != latest_file:
        print "Expected latest.txt: %s, got %s" % (latest, latest_file)
        ok = False

    return ok

def check_firmware():
    ok = True
    releases = json.loads(open('firmware/releases.json', 'r').read())
    for r in releases:
        firmware = r['url'][len('/data/'):]
        version = '.'.join([ str(x) for x in r['version'] ])

        if version not in firmware:
            print "Missing '%s' in '%s'" % (version, firmware)
            ok = False

        if not os.path.exists(firmware):
            print "Missing firmware file", firmware
            ok = False

    return ok

if __name__ == '__main__':
    ok = True
    ok &= check_plugin()
    ok &= check_firmware()

    if ok:
        print "EVERYTHING IS OK"
        exit(0)
    else:
        print "SOME PROBLEMS FOUND"
        exit(1)
