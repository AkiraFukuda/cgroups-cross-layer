import numpy as np
from scipy import fft

amp_low_ratio = 0.25
freq_high_ratio = 1

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
    return list(np.abs(new_sig)), yf

bw_hdd_record = [100, 101, 100, 100, 99, 100, 45, 101, 57, 100, 53, 101]

bw_p, yf = noise_prediction(120, 10)

print(bw_p)