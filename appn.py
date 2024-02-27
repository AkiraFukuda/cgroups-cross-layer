import sys, time, random
from datetime import datetime
from pytz import timezone
import numpy as np
from scipy import fft

# estimation parameters
amp_low_ratio = 0.25
freq_high_ratio = 1
bw_low_bound = 40
bw_high_bound = 100

# collision detection parameters
pre_read_ratio = 0.05
bw_high_bound_col = 60
exp_base = 0.5

hdd_source = "/home/cc/mnt/"
ssd_source = "/home/cc/ssd/"
ssd_io_size = 96

bw_record = []
io_time_record = []
timestep_record = []
aug_record = []
bw_hdd_record = []

def noise_prediction(window_length, interval):
    N = int(window_length / interval)
    y = bw_hdd_record[-N:]
    mean = np.mean(y)
    y_new = np.array(y) - mean
    xf = fft.fftfreq(N, 1/N)
    yf = fft.fft(y_new)
    amp = np.abs(yf)
    amp_low_threshold = np.max(amp) * amp_low_ratio
    freq_high_threshold = np.max(xf) * freq_high_ratio
    yf_filtered = []
    for i in range(len(yf)):
        if amp[i] > amp_low_threshold and np.abs(xf[i]) < freq_high_threshold:
            yf_filtered.append(yf[i])
        else:
            yf_filtered.append(0)
    new_sig = fft.ifft(yf_filtered)
    new_sig = new_sig + mean
    return list(np.abs(new_sig))

def read_with_no_control(app_tag, size, interval, exp_time):
    global bw_record, io_time_record, aug_record, bw_hdd_record
    gstart = time.time()
    for i in range(int(exp_time/interval)):
        tmp = time.time() - gstart
        timestep_record.append(tmp)
        print("%.2f s"% tmp)
        hdd_name = hdd_source + app_tag + ".bin"
        ssd_name = ssd_source + app_tag + ".bin"

        start = time.time()
        f = open(hdd_name, "rb")
        f.read(size*1024*1024)
        f.close()
        io_time_hdd = time.time() - start
        f = open(ssd_name, "rb")
        f.read(ssd_io_size*1024*1024)
        f.close()
        io_time_all = time.time() - start

        bw_hdd = size / io_time_hdd
        bw_all = (size + ssd_io_size) / io_time_all
        bw_record.append(bw_all)
        io_time_record.append(io_time_all)
        aug_record.append(1.0)
        bw_hdd_record.append(bw_hdd)

        ana_time = time.time() - start
        print("Time = %.2f s, Bw_hdd = %.2f MB/s, Bw_all = %.2f MB/s" % (ana_time, bw_hdd, bw_all))
        time.sleep(interval)
    
    return np.mean(bw_hdd_record)

accuracy_threshold = 0.1
def read_with_prediction(app_tag, size, interval, exp_time, predict_result, bw_per_second):
    global bw_record, io_time_record, aug_record, bw_hdd_record
    phase_chg = 0
    pred_error = 0
    sum_bw_hdd = 0
    count = 0
    new_preds = []
    gstart = time.time()
    N = int(exp_time/interval)
    for i in range(N):
        tmp = time.time() - gstart
        timestep_record.append(tmp)
        print("%.2f s"% tmp)
        hdd_name = hdd_source + app_tag + ".bin"
        ssd_name = ssd_source + app_tag + ".bin"

        print("Predict:", predict_result[i])

        if i > 0:
            phase_chg2 = phase_chg
            while phase_chg2 > interval:
                phase_chg2 -= interval
                i -= 1
            bw_predicted = predict_result[i] + (phase_chg2 / interval) * (predict_result[i-1] - predict_result[i])
        else:
            bw_predicted = predict_result[i]
        print("New predict:", bw_predicted)
        new_preds.append(bw_predicted)

        if bw_predicted < bw_low_bound:
            aug_ratio = 0.0
        elif bw_predicted > bw_high_bound:
            aug_ratio = 1.0
        else:
            aug_ratio = (bw_predicted - bw_low_bound) / (bw_high_bound - bw_low_bound)

        print("Augmentation = {:.0%}".format(aug_ratio))
        
        phase_chg += (1-aug_ratio) * size / bw_per_second
        print('Phase change:', phase_chg)

        start = time.time()
        f = open(hdd_name, "rb")
        f.read(int(size*aug_ratio*1024*1024))
        f.close()
        io_time_hdd = time.time() - start
        f = open(ssd_name, "rb")
        f.read(ssd_io_size*1024*1024)
        f.close()
        io_time_all = time.time() - start
        
        bw_hdd = size*aug_ratio / io_time_hdd
        bw_all = (size*aug_ratio + ssd_io_size) / io_time_all
        bw_record.append(bw_all)
        io_time_record.append(io_time_all)
        aug_record.append(aug_ratio)
        bw_hdd_record.append(bw_hdd)
        sum_bw_hdd += bw_hdd
        count += 1

        pred_error += (bw_hdd - bw_predicted) ** 2
        pred_RMSE = np.sqrt(pred_error) / (i+1)
        pred_accuracy = pred_RMSE / (sum_bw_hdd / count)
        if pred_accuracy > accuracy_threshold:
            new_predict_result = noise_prediction(exp_time, interval)
            print("New Prediction =", new_predict_result)
            tmp = 0
            for ii in new_predict_result:
                if i+tmp < N:
                    predict_result[i+tmp] = ii
                    tmp += 1
            pred_error = 0
            sum_bw_hdd = 0
            count = 0

        ana_time = time.time() - start
        print("Time = %.2f s, Bw_hdd = %.2f MB/s, Bw_all = %.2f MB/s" % (ana_time, bw_hdd, bw_all))
        time.sleep(interval)
    
    print("Updated prediction:", new_preds)

def read_with_collision_detection(app_tag, size, interval, exp_time):
    global bw_record, io_time_record, aug_record, bw_hdd_record
    col_record = []
    bw_pre = bw_high_bound
    gstart = time.time()
    for i in range(int(exp_time/interval)):
        tmp = time.time() - gstart
        timestep_record.append(tmp)
        print("%.2f s"% tmp)
        hdd_name = hdd_source + app_tag + ".bin"
        ssd_name = ssd_source + app_tag + ".bin"

        if bw_pre > bw_high_bound_col:
            random_factor = 1
        else:
            # random_factor = bw_pre / bw_high_bound_col # fixed random factor
            random_factor = random.uniform(1, bw_pre / bw_high_bound_col) # real random factor
        print("Collision Factor: ", random_factor)
        hdd_io_size = size * random_factor
        col_record.append(random_factor)
        
        start = time.time()
        f = open(hdd_name, "rb")
        f.read(int(hdd_io_size*1024*1024))
        f.close()
        end = time.time()
        hdd_io_time = end - start
        
        f = open(ssd_name, "rb")
        f.read(int(ssd_io_size*1024*1024))
        f.close()

        io_time_all = time.time() - start
        io_time_record.append(io_time_all)
        
        bw_hdd = hdd_io_size / hdd_io_time
        bw_all = (hdd_io_size + ssd_io_size) / io_time_all
        bw_record.append(bw_all)
        aug_ratio = hdd_io_size / size
        aug_record.append(aug_ratio)
        bw_hdd_record.append(bw_hdd)
        bw_pre = bw_all
        
        ana_time = time.time() - start
        print("Time = %.2f s, Bw_hdd = %.2f MB/s, Bw_all = %.2f MB/s" % (ana_time, bw_hdd, bw_all))
        time.sleep(interval)
    
    return col_record

def read_with_collision_detection_twice(app_tag, size, interval, exp_time):
    global bw_record, io_time_record, aug_record, bw_hdd_record
    bw_high_bound_col = 100
    col_record = []
    gstart = time.time()
    for i in range(int(exp_time/interval)):
        tmp = time.time() - gstart
        timestep_record.append(tmp)
        print("%.2f s"% tmp)
        hdd_name = hdd_source + app_tag + ".bin"
        ssd_name = ssd_source + app_tag + ".bin"

        pre_size = size * pre_read_ratio
        after_size = size - pre_size

        start1 = time.time()
        f = open(hdd_name, "rb")
        f.read(int(pre_size*1024*1024))
        f.close()
        end1 = time.time()
        pre_io_time = end1 - start1
        bw_pre = pre_size / pre_io_time

        if bw_pre > bw_high_bound_col:
            random_factor = 1
        else:
            # random_factor = bw_pre / bw_high_bound_col # fixed random factor
            random_factor = min(1, random.expovariate(bw_high_bound_col / (bw_pre+0.01))) # real random factor
        print("Collision Factor: ", random_factor)
        after_size *= random_factor
        col_record.append(random_factor)
        
        start2 = time.time()
        f = open(hdd_name, "rb")
        f.read(int(after_size*1024*1024))
        f.close()
        end2 = time.time()
        after_io_time = end2 - start2
        
        f = open(ssd_name, "rb")
        f.read(int(ssd_io_size*1024*1024))
        f.close()

        io_time_all = time.time() - start1
        io_time_record.append(io_time_all)
        
        bw_hdd = (pre_size + after_size) / (pre_io_time + after_io_time)
        bw_all = (pre_size + after_size + ssd_io_size) / io_time_all
        bw_record.append(bw_all)
        aug_ratio = (pre_size + after_size) / size
        aug_record.append(aug_ratio)
        bw_hdd_record.append(bw_hdd)
        
        ana_time = time.time() - start1
        print("Time = %.2f s, Bw_hdd = %.2f MB/s, Bw_all = %.2f MB/s" % (ana_time, bw_hdd, bw_all))
        time.sleep(interval)
    
    return col_record

# def read_with_collision_detection_twice_no_random(app_tag, size, interval, exp_time):
#     global bw_record, io_time_record, aug_record, bw_hdd_record
#     bw_high_bound_col = 100
#     col_record = []
#     gstart = time.time()
#     for i in range(int(exp_time/interval)):
#         tmp = time.time() - gstart
#         timestep_record.append(tmp)
#         print("%.2f s"% tmp)
#         hdd_name = hdd_source + app_tag + ".bin"
#         ssd_name = ssd_source + app_tag + ".bin"

#         pre_size = size * pre_read_ratio
#         after_size = size - pre_size

#         start1 = time.time()
#         f = open(hdd_name, "rb")
#         f.read(int(pre_size*1024*1024))
#         f.close()
#         end1 = time.time()
#         pre_io_time = end1 - start1
#         bw_pre = pre_size / pre_io_time

#         if bw_pre > bw_high_bound_col:
#             random_factor = 1
#         else:
#             random_factor = bw_pre / bw_high_bound_col # fixed random factor
#             # random_factor = min(1, random.expovariate(bw_high_bound_col / (bw_pre+0.01))) # real random factor
#         print("Collision Factor: ", random_factor)
#         after_size *= random_factor
#         col_record.append(random_factor)
        
#         start2 = time.time()
#         f = open(hdd_name, "rb")
#         f.read(int(after_size*1024*1024))
#         f.close()
#         end2 = time.time()
#         after_io_time = end2 - start2
        
#         f = open(ssd_name, "rb")
#         f.read(int(ssd_io_size*1024*1024))
#         f.close()

#         io_time_all = time.time() - start1
#         io_time_record.append(io_time_all)
        
#         bw_hdd = (pre_size + after_size) / (pre_io_time + after_io_time)
#         bw_all = (pre_size + after_size + ssd_io_size) / io_time_all
#         bw_record.append(bw_all)
#         aug_ratio = (pre_size + after_size) / size
#         aug_record.append(aug_ratio)
#         bw_hdd_record.append(bw_hdd)
        
#         ana_time = time.time() - start1
#         print("Time = %.2f s, Bw_hdd = %.2f MB/s, Bw_all = %.2f MB/s" % (ana_time, bw_hdd, bw_all))
#         time.sleep(interval)
    
#     return col_record

# accuracy_threshold = 0.3
# def read_with_combined(app_tag, size, interval, exp_time, predict_result, bw_per_second):
#     global bw_record, io_time_record, aug_record, bw_hdd_record
#     method_count = []
#     new_preds = []

#     pred_accuracy = 1
#     phase_chg = 0
#     bw_pre = bw_high_bound
    
#     gstart = time.time()
#     for i in range(int(exp_time/interval)):
#         tmp = time.time() - gstart
#         timestep_record.append(tmp)
#         print("%.2f s"% tmp)
#         hdd_name = hdd_source + app_tag + ".bin"
#         ssd_name = ssd_source + app_tag + ".bin"

#         bw_predicted = predict_result[i]
#         if i > 0:
#             phase_chg2 = phase_chg
#             while phase_chg2 > interval:
#                 phase_chg2 -= interval
#                 i -= 1
#             bw_predicted = predict_result[i] + (phase_chg2 / interval) * (predict_result[i] - predict_result[i-1])
#         else:
#             bw_predicted = predict_result[i]
#         print("New predict:", bw_predicted)
#         new_preds.append(bw_predicted)

#         if pred_accuracy > 1 - accuracy_threshold:
#             if bw_predicted < bw_low_bound:
#                 aug_ratio = 0.0
#             elif bw_predicted > bw_high_bound:
#                 aug_ratio = 1.0
#             else:
#                 aug_ratio = (bw_predicted - bw_low_bound) / (bw_high_bound - bw_low_bound)
#             method_count.append(1)
#         else:
#             if bw_pre > bw_high_bound_col:
#                 random_factor = 1
#             else:
#             # random_factor = bw_pre / bw_high_bound_col # fixed random factor
#                 random_factor = min(1, random.expovariate(bw_high_bound_col / (bw_pre+0.01))) # real random factor
#                 # print("Collision Factor: ", random_factor)
#                 aug_ratio = random_factor
#             method_count.append(0)

#         print("Augmentation = {:.0%}".format(aug_ratio))

#         phase_chg += (1-aug_ratio) * size / bw_per_second

#         start = time.time()
#         f = open(hdd_name, "rb")
#         f.read(int(size*aug_ratio*1024*1024))
#         f.close()
#         io_time_hdd = time.time() - start
#         f = open(ssd_name, "rb")
#         f.read(ssd_io_size*1024*1024)
#         f.close()
#         io_time_all = time.time() - start
        
#         bw_hdd = size*aug_ratio / io_time_hdd
#         bw_all = (size*aug_ratio + ssd_io_size) / io_time_all
#         bw_record.append(bw_all)
#         io_time_record.append(io_time_all)
#         aug_record.append(aug_ratio)
#         bw_hdd_record.append(bw_hdd)
#         bw_pre = bw_hdd

#         ana_time = time.time() - start
#         print("Time = %.2f s, Bw_hdd = %.2f MB/s, Bw_all = %.2f MB/s" % (ana_time, bw_hdd, bw_all))
        
#         pred_accuracy = bw_hdd / bw_predicted
#         time.sleep(interval)
    
#     print("Updated prediction:", new_preds)
#     print("Method:", method_count)

def work(app_tag, read_size, interval, exp_time, ratio):
    st_time = time.time()
    bw_per_second = read_with_no_control(app_tag, read_size, interval, exp_time)
    bw_predicted = noise_prediction(exp_time, interval)
    print("bw_predicted =", bw_predicted)
    while True:
        if time.time() - st_time >= exp_time*ratio:
            read_with_no_control(app_tag, read_size, interval, exp_time)
            break
    while True:
        if time.time() - st_time >= exp_time*ratio*2:
            read_with_prediction(app_tag, read_size, interval,
                                exp_time, bw_predicted, bw_per_second)
            break
    # while True:
    #     if time.time() - st_time >= exp_time*ratio*3:
    #         col_record = read_with_collision_detection(app_tag, read_size,
    #                                                 interval, exp_time)
    #         break
    while True:
        if time.time() - st_time >= exp_time*ratio*3:
            col_record = read_with_collision_detection_twice(app_tag, read_size,
                                                    interval, exp_time)
            break
    # while True:
    #     if time.time() - st_time >= exp_time*ratio:
    #         col_record = read_with_combined(app_tag, read_size, interval,
    #                                         exp_time, bw_predicted, bw_per_second)
    #         break

    print("bw =", bw_record)
    print("io_time =", io_time_record)
    print("augment =", aug_record)
    print("bw_hdd =", bw_hdd_record)
    print("timestep =", timestep_record)
    # print("collision =", col_record)

# def compare(app_tag, read_size, interval, exp_time, ratio):
#     st_time = time.time()
#     # bw_per_second = read_with_no_control(app_tag, read_size, interval, exp_time)
#     # bw_predicted = noise_prediction(exp_time, interval)
#     # print("bw_predicted =", bw_predicted)
#     col_record = read_with_collision_detection_twice(app_tag, read_size,
#                                                     interval, exp_time)
#     while True:
#         if time.time() - st_time >= exp_time*ratio:
#             col_record = read_with_collision_detection_twice_no_random(app_tag, read_size,
#                                                     interval, exp_time)
#             break
#     print("bw =", bw_record)
#     print("io_time =", io_time_record)
#     print("augment =", aug_record)
#     print("bw_hdd =", bw_hdd_record)

def main():
    app_tag = sys.argv[1]
    read_size = int(sys.argv[2])
    interval = int(sys.argv[3])
    exp_time = int(sys.argv[4])
    time_ratio = 2
    if sys.argv[5] == 'now':
        work(app_tag, read_size, interval, exp_time, time_ratio)
    else:
        while True:
            now_time = datetime.now(timezone('UTC'))
            if now_time.hour == int(sys.argv[5]) and now_time.minute == int(sys.argv[6]) and now_time.second == int(sys.argv[7]):
                work(app_tag, read_size, interval, exp_time, time_ratio)
                break

if __name__ == "__main__":
    main()

