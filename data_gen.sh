#!/bin/bash
dd if=/dev/urandom of="/home/cc/mnt/a1.bin" bs=1M count=4096
dd if=/dev/urandom of="/home/cc/mnt/a2.bin" bs=1M count=4096
dd if=/dev/urandom of="/home/cc/mnt/a3.bin" bs=1M count=4096
dd if=/dev/urandom of="/home/cc/mnt/a4.bin" bs=1M count=4096
dd if=/dev/urandom of="/home/cc/mnt/n1.bin" bs=1M count=16384
dd if=/dev/urandom of="/home/cc/mnt/n2.bin" bs=1M count=16384
dd if=/dev/urandom of="/home/cc/mnt/n3.bin" bs=1M count=16384
dd if=/dev/urandom of="/home/cc/mnt/n4.bin" bs=1M count=16384
