import threading
import sys

from yfs_server import YFS

def user_interface(yfs: YFS): 
    while True:
        print("Menu:")
        print("1. Read [filename]")
        print("2. Write [filename] + [content]")
        print("3. Exit")

        user_commands = input("Input command: ").split()
        command = user_commands[0].lower()

        if command == "exit":
            return
        
        args = user_commands[1:]
        
        if command == "read":
            yfs.read(args[0])

        if command == "write":
            if len(args) == 2:
                yfs.write(args[0], args[1])
            else:
                print("Command is incorrect")
      
if __name__ == "__main__":
    pid = int(sys.argv[1])
    server = YFS(pid)
    #to-do in future: need refine yfs server: remove userinterface function inside yfs server and move it to user_interface
    server_thread = threading.Thread(target=server.serve)
    user_interface_thread = threading.Thread(target=user_interface, args=(server,))
    #to-do: fix bug can not completely exit
    server_thread.start()
    user_interface_thread.start()