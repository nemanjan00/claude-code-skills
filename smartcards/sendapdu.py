#!/usr/bin/env python3
"""Send a list of APDUs to a PC/SC smart card and print the responses.

Requires a PC/SC stack (pcscd) and pyscard:  pip install pyscard

Usage:
    sendapdu.py [--reader N] [--gr] [--stop] "00 A4 04 00 00" "00 CA 9F 7F 00" ...
    printf '00 A4 04 00 00\\n80 CA 9F 7F 00\\n' | sendapdu.py --gr

Options:
    --reader N   use reader index N (default 0)
    --gr         on '61 XX', automatically issue GET RESPONSE (00 C0 00 00 XX) and append the data
    --stop       stop at the first non-9000 status word
Lines/args are hex; spaces optional; '#' starts a comment.
"""
import sys
import re


def parse_hex(s):
    s = s.split("#", 1)[0]
    return [int(b, 16) for b in re.findall(r'[0-9A-Fa-f]{2}', s)]


def main():
    args = sys.argv[1:]
    reader_idx, do_gr, stop = 0, False, False
    apdus = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--reader":
            reader_idx = int(args[i + 1]); i += 2
        elif a == "--gr":
            do_gr = True; i += 1
        elif a == "--stop":
            stop = True; i += 1
        else:
            apdus.append(a); i += 1
    if not apdus and not sys.stdin.isatty():
        apdus = [ln for ln in sys.stdin.read().splitlines() if ln.strip()]

    from smartcard.System import readers
    from smartcard.util import toHexString

    rs = readers()
    if not rs:
        sys.exit("no PC/SC readers found (is pcscd running / a reader attached?)")
    print(f"reader: {rs[reader_idx]}")
    conn = rs[reader_idx].createConnection()
    conn.connect()
    print("ATR:", toHexString(conn.getATR()))

    for raw in apdus:
        cmd = parse_hex(raw)
        if not cmd:
            continue
        print("->", toHexString(cmd))
        data, sw1, sw2 = conn.transmit(cmd)
        if do_gr and sw1 == 0x61:                       # more data available
            more, sw1, sw2 = conn.transmit([0x00, 0xC0, 0x00, 0x00, sw2])
            data += more
        if do_gr and sw1 == 0x6C:                       # wrong Le, retry with SW2
            data, sw1, sw2 = conn.transmit(cmd[:4] + [sw2])
        print(f"<- {toHexString(data)}  SW={sw1:02X}{sw2:02X}"
              f"{'  <- not 9000' if (sw1, sw2) != (0x90, 0x00) else ''}")
        if stop and (sw1, sw2) != (0x90, 0x00):
            print("stopping."); break

    conn.disconnect()


if __name__ == "__main__":
    main()
