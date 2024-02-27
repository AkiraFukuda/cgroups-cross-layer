import sys, time, random
from datetime import datetime
from pytz import timezone
import numpy as np

def main():
    interval = int(sys.argv[1])
    value = random.expovariate(1.0 / interval)
    print(int(value))

if __name__ == "__main__":
    main()