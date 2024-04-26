import threading
import sys
from time import sleep

from yfs_server import YFS
from testcases import testcases

def user_interface(yfs: YFS):
    for testcase in testcases:
        if testcase.is_read():
            yfs.read(testcase.file)
        elif testcase.is_write():
            yfs.write(testcase.file, testcase.content)
        sleep(0.5)
      
if __name__ == "__main__":
    pid = sys.argv[1]
    #to-do: fix bug can not completely exit
    server = YFS(pid)
    #to-do in future: need refine yfs server: remove userinterface function inside yfs server and move it to user_interface
    server_thread = threading.Thread(target=server.serve)
    user_interface_thread = threading.Thread(target=user_interface, args=(server,))
    sleep(0.2 * int(pid))
    server_thread.start()
    user_interface_thread.start()