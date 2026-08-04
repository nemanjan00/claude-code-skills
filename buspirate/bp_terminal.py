#!/usr/bin/env python3
"""Minimal robust driver for the Bus Pirate 5/6 VT100 terminal (fallback when BPIO2 is unavailable).

Prefer BPIO2 (the binary interface on the 2nd USB serial port) for real scripting; this class exists
for interactive/one-off use. Requires: pip install pyserial.

    from bp_terminal import BusPirate
    bp = BusPirate("/dev/ttyACM0")   # the *terminal* port (if00)
    bp.wake()                        # DTR toggle + answer the VT100 prompt
    print(bp.cmd("i"))               # version/info
    bp.close()
"""
import re
import time
import serial

_ANSI = re.compile(rb'\x1b\[[0-9;?]*[A-Za-z]')


def _clean(b: bytes) -> str:
    return _ANSI.sub(b"", b).replace(b"\x07", b"").decode("latin1")


class BusPirate:
    def __init__(self, port="/dev/ttyACM0", baud=115200):
        # NOTE: never open at 1200 baud on RP2040/RP2350 — that triggers the BOOTSEL bootloader.
        self.s = serial.Serial()
        self.s.port = port
        self.s.baudrate = baud
        self.s.timeout = 0.05
        self.s.open()
        self.s.dtr = True
        self.s.rts = True
        self.buf = ""

    def _read(self):
        n = self.s.in_waiting
        if n:
            self.buf += _clean(self.s.read(n))

    def expect(self, subs, timeout=8.0):
        """Read until any substring in `subs` appears in the buffer. Returns its index, or -1."""
        if isinstance(subs, str):
            subs = [subs]
        t0 = time.time()
        while time.time() - t0 < timeout:
            self._read()
            for i, su in enumerate(subs):
                if su in self.buf:
                    return i
            time.sleep(0.04)
        return -1

    def send(self, line: str):
        self.buf = ""
        self.s.write(line.encode() + b"\r")

    def wake(self):
        """Toggle DTR to trigger the boot banner, then answer the VT100 colour prompt with 'n'
        (plain text is easier to parse). Call once after connecting."""
        self.s.dtr = False
        time.sleep(0.35)
        self.s.dtr = True
        self.expect(["(Y/n)>", "HiZ>", "HDUART>", "SPI>", "I2C>", "UART>"], 10)
        if "(Y/n)>" in self.buf:
            self.send("n")
            self.expect([">"], 6)

    def cmd(self, line: str, settle=1.2, total=8.0) -> str:
        """Send a command and return the cleaned response once the port goes quiet.
        The Bus Pirate terminal has high, variable latency — this reads until `settle` seconds
        of silence (or `total` timeout) rather than a fixed sleep."""
        self.send(line)
        time.sleep(0.1)
        t0 = time.time()
        last = time.time()
        while time.time() - t0 < total:
            if self.s.in_waiting:
                self._read()
                last = time.time()
            elif self.buf and time.time() - last > settle:
                break
            else:
                time.sleep(0.04)
        return self.buf

    @staticmethod
    def rx_bytes(text: str):
        """Extract the *real* received bytes from terminal output: the async `0xNN` tokens printed
        after a mode prompt (e.g. `HDUART> 0x3b 0x9e ...`). Ignores `TX:` echoes, the command echo,
        and `(No data to read)` placeholders — the classic terminal read-parsing gotcha."""
        out = []
        for ln in text.splitlines():
            if "TX:" in ln or "[" in ln:
                continue
            m = re.search(r'>\s*(0x[0-9A-Fa-f]{2}.*)', ln)
            src = m.group(1) if m else (ln if ">" not in ln else "")
            src = src.replace("(No data to read)", "")
            out += re.findall(r'0x([0-9A-Fa-f]{2})', src)
        return [b.lower() for b in out]

    def close(self):
        self.s.close()
