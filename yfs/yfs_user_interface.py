import threading
import sys

from yfs_server import YFS

def user_interface(yfs: YFS): 
    while True:
        user_commands = input().split()
        command = user_commands[0].lower()

        if command == "exit":
            return
        
        args = user_commands[1:]
        
        if command == "read":
            content = yfs.read(args[0])
            if content is not None:
                print(content)

        if command == "write":
            if len(args) >= 2:
                content = " ".join(args[1:])
                yfs.write(args[0], content)
            else:
                print("Command is incorrect")
      
if __name__ == "__main__":
    pid = sys.argv[1]
    #to-do: fix bug can not completely exit
    print("Menu:")
    print("1. Read [filename]")
    print("2. Write [filename] + [content]")
    print("3. Exit")
    server = YFS(pid)
    #to-do in future: need refine yfs server: remove userinterface function inside yfs server and move it to user_interface
    server_thread = threading.Thread(target=server.serve)
    user_interface_thread = threading.Thread(target=user_interface, args=(server,))
    server_thread.start()
    user_interface_thread.start()