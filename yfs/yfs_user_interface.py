import threading
import sys

from yfs_server import YFS

def user_interface(yfs: YFS): 
    while True:
        print("Menu:")
        print("1. Read File + [filename]")
        print("2. Write File + [filename] + [content]")
        print("3. Exit")

        user_commands = input("Input command: ").split()
        command = user_commands[0].lower()

        if command == "exit":
            return
        
        args = user_commands[1:]
        
        if command == "read":
            #Error
            #yfs.send_read(arg)
            content = yfs.read_file(args)
            print("Content:", content)

        if command == "write":
            if len(user_commands) > 2:
                content = user_commands[2]
                yfs.write_file(args, content)
                #Error
                #yfs.send_write(arg, content)
                print("Send Write")
            else:
                print("Command is incorrect")
      
if __name__ == "__main__":
    pid = int(sys.argv[1])
    server = YFS(pid)
    
    server_thread = threading.Thread(target=server.serve)
    user_interface_thread = threading.Thread(target=user_interface, args=(server,))

    server_thread.start()
    user_interface_thread.start()   