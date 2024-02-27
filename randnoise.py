import sys, time, random
from datetime import datetime
from pytz import timezone
import numpy as np

def random_read(filename, size, interval, exp_time):
    bandwidth = []
    gstart = time.time()
    nowtime = gstart
    while nowtime - gstart < exp_time:
        real_size = np.random.poisson(lam=size)
        nowtime = time.time()
        print("Start at %.2f s" % (nowtime - gstart))
        start = time.time()
        f = open(filename, "rb")
        f.read(real_size*1024*1024)
        f.close()
        io_time = time.time() - start
        bw = real_size / io_time
        bandwidth.append(bw)
        ana_time = time.time() - start
        print("T = %.2f s, Bw = %.2f MB/s" % (ana_time, bw))
        factor = random.expovariate(1.0 / interval)
        time.sleep(factor)
    
    return bandwidth

def work(app_tag, read_size, interval, exp_time):
    filename = "/home/cc/mnt/" + app_tag + ".bin"
    bw_record = random_read(filename, read_size, interval, exp_time)
    print(bw_record)

def main():
    app_tag = sys.argv[1]
    read_size = int(sys.argv[2])
    interval = int(sys.argv[3])
    exp_time = int(sys.argv[4])
    if sys.argv[5] == 'now':
        work(app_tag, read_size, interval, exp_time)
    else:
        while True:
            now_time = datetime.now(timezone('UTC'))
            if now_time.hour == int(sys.argv[5]) and now_time.minute == int(sys.argv[6]) and now_time.second == int(sys.argv[7]):
                work(app_tag, read_size, interval, exp_time)
                break


if __name__ == "__main__":
    main()