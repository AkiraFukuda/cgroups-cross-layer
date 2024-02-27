import sys, time
from datetime import datetime
from pytz import timezone

filename = "/home/cc/mnt/n1.bin"
bandwidth = []
size = 16384
while True:
    start = time.time()
    f = open(filename, "rb")
    f.read(size*1024*1024)
    f.close()
    io_time = time.time() - start
    bw = size / io_time
    bandwidth.append(bw)
    ana_time = time.time() - start
    print("16GB: T = %.2f s, Bw = %.2f MB/s" % (ana_time, bw))
    time.sleep(1)
