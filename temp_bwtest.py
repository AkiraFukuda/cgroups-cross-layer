import sys, time

filename = "/home/cc/mnt/a2.bin"

def work(size):
    start = time.time()
    f = open(filename, "rb")
    f.read(size*1024*1024)
    f.close()
    io_time = time.time() - start
    bw = size / io_time
    ana_time = time.time() - start
    print("%d MB: T = %.2f s, Bw = %.2f MB/s" % (size, ana_time, bw))
    time.sleep(1)

    return bw

def main():
    bws = [0] * 11
    for i in range(11):
        bws[i] = work(2**i)
    print("Bw:", bws)

if __name__ == "__main__":
    main()