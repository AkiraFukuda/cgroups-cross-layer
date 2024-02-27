import sys, time, random
from datetime import datetime
from pytz import timezone
import numpy as np

def main():
    low = int(sys.argv[1])
    high = int(sys.argv[2])
    value = random.uniform(low, high)
    print(int(value))

if __name__ == "__main__":
    main()