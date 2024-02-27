import sys, time
from datetime import datetime
from pytz import timezone

def fully_read(filename, size, interval, exp_time):
    bandwidth = []
    gstart = time.time()
    for i in range(int(exp_time/interval)):
        tmp = time.time() - gstart
        print("%.2f s"% tmp)

        start = time.time()
        f = open(filename, "rb")
        f.read(size*1024*1024)
        f.close()
        io_time = time.time() - start
        bw = size / io_time
        bandwidth.append(bw)
        ana_time = time.time() - start
        print("T = %.2f s, Bw = %.2f MB/s" % (ana_time, bw))
        time.sleep(interval - ana_time)
    
    return bandwidth

def work(app_tag, read_size, interval, exp_time, run_times, ratio):
    filename = "/home/cc/mnt/" + app_tag + ".bin"
    st_time = time.time()
    bw_record = fully_read(filename, read_size, interval, exp_time)
    print(bw_record)
    for i in range(0, run_times):
        print(i)
        while True:
            if time.time() - st_time >= exp_time*ratio*(i+1):
                bw_record = fully_read(filename, read_size, interval, exp_time)
                print(bw_record)
                break

def main():
    app_tag = sys.argv[1]
    read_size = int(sys.argv[2])
    interval = int(sys.argv[3])
    exp_time = int(sys.argv[4])
    run_times = int(sys.argv[5])
    time_ratio = 1.2
    if sys.argv[6] == 'now':
        work(app_tag, read_size, interval, exp_time, run_times, time_ratio)
    else:
        while True:
            now_time = datetime.now(timezone('UTC'))
            if now_time.hour == int(sys.argv[6]) and now_time.minute == int(sys.argv[7]) and now_time.second == int(sys.argv[8]):
                work(app_tag, read_size, interval, exp_time, run_times, time_ratio)
                break


if __name__ == "__main__":
    main()