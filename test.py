import sys
from time import sleep

if __name__ == "__main__":
    pid = int(sys.argv[1])
    for i in range(100):
        print(f"{pid}: {i}")
        sleep(pid)