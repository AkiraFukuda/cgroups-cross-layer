import sys, time
from datetime import datetime
from pytz import timezone

def fully_read(filename, size, interval, exp_time):
    bandwidth = []
    for i in range(int(exp_time/interval)):
        print("%s s"%(i*interval))

        start = time.time()
        f = open(filename, "rb")
        f.read(size*1024*1024)
        f.close()
        io_time = time.time() - start
        bw = size / io_time
        bandwidth.append(bw)
        ana_time = time.time() - start
        print("T = %.2f s, Bw = %.2f MB/s" % (ana_time, bw))
        if io_time > interval:
            print("Analysis time is larger than the interval!")
        time.sleep(interval - ana_time)
    
    return bandwidth

def work(app_tag, read_size, interval, exp_time):
    filename = "/home/cc/mnt/" + app_tag + ".bin"
    bw_record = fully_read(filename, read_size, interval, exp_time)
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