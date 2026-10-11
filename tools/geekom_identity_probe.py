#!/usr/bin/env python3
"""Probe documented identity routes; never upload firmware or capture fingers."""
import ctypes
import os
import time

class Step(ctypes.Structure):
    _fields_ = [('length', ctypes.c_uint32), ('delay', ctypes.c_uint16),
                ('cs_change', ctypes.c_uint8), ('flags', ctypes.c_uint8)]

class Request(ctypes.Structure):
    _fields_ = [('n', ctypes.c_uint32), ('mode', ctypes.c_uint32),
                ('speed', ctypes.c_uint32), ('pre_delay', ctypes.c_uint32),
                ('steps', Step * 16), ('tx', ctypes.c_ubyte * 16384),
                ('rx', ctypes.c_ubyte * 16384)]

libc = ctypes.CDLL(None, use_errno=True)
libc.ioctl.argtypes = [ctypes.c_int, ctypes.c_ulong, ctypes.c_void_p]
libc.ioctl.restype = ctypes.c_int

def ioctl(fd, command, arg=None):
    result = libc.ioctl(fd, command, arg)
    if result < 0:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err))

def exchange(fd, mode, speed, packet, length=0, split=False):
    request = Request()
    request.mode, request.speed = mode, speed
    request.tx[:len(packet)] = packet
    if split and length:
        request.n = 2
        request.steps[0] = Step(len(packet), 0, 0, 2)
        request.steps[1] = Step(length, 0, 0, 1)
    else:
        request.n = 1
        request.steps[0] = Step(len(packet) + length, 0, 0, 0)
    ioctl(fd, 0x80A0, ctypes.byref(request))
    return bytes(request.rx[len(packet):len(packet) + length])

def main():
    fd = os.open('/dev/focal_moh_spi', os.O_RDWR | os.O_CLOEXEC)
    try:
        for speed in (1000000, 100000):
            for mode in (0, 4, 1, 5, 2, 6, 3, 7):
                ioctl(fd, 0x8086)
                for split in (True, False):
                    exchange(fd, mode, speed, bytes.fromhex('ff 00 00 00'))
                    time.sleep(0.02)
                    replies = [exchange(fd, mode, speed,
                                        bytes.fromhex('91 80 00 20 00 00 00'),
                                        32, split) for _ in range(2)]
                    chip = int.from_bytes(replies[0][19:21], 'big')
                    print(f'mode={mode} speed={speed} split={split} '
                          f'chip={chip:04x} stable={replies[0] == replies[1]} '
                          f'info={replies[0].hex()}', flush=True)
                    if chip == 0x9368 and replies[0] == replies[1] and replies[0][23:25] == bytes((64, 80)):
                        print('PASS: repeatable FT9368 identity and geometry', flush=True)
                        return 0
        print('FAIL: no validated FT9368 identity', flush=True)
        return 1
    finally:
        os.close(fd)

if __name__ == '__main__':
    raise SystemExit(main())
