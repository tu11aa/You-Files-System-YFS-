import os
import socket
from datetime import datetime
import threading
import math
import sys

from message import Message, MessageType
from yfs_logger import YFSLogger

def is_lesser_vector(vector1, vector2):

    # Tính độ dài của hai vector
    length_vector1 = math.sqrt(sum([x ** 2 for x in vector1]))
    length_vector2 = math.sqrt(sum([x ** 2 for x in vector2]))

    # So sánh độ dài của hai vector
    return length_vector1 <= length_vector2

class YFS:
    HOST = '0.0.0.0'
    PORT = 8080

    def __init__(self, pid: int) -> None:
        self.pid = pid
        self.peer_to_address = {}
        self.vp = {}
        self.timestamps = [datetime.now().timestamp()]
        self.queue = []
        self.__main_dir = self.get_main_dir()
        self.logger = YFSLogger()

        self.readers = []

        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receiver.bind((YFS.HOST, YFS.PORT))
        # self.receiver.listen(5)

        self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.send_SES_message(-1, socket.gethostbyname(socket.gethostname()), MessageType.BROADCAST)

    def send_SES_message(self, receiver: int, message: str, message_type: int):
        #Update self
        self.timestamps[self.pid] = datetime.now().timestamp()

        #to-do: send message to receiver
        message = Message(self.pid, receiver, message, self.timestamps, self.vp, message_type)
        if (message_type == MessageType.BROADCAST):
            address = ('<broadcast>', YFS.PORT)
        else:
            address = (self.peer_to_address[receiver], YFS.PORT)
        self.sender.sendto(str(message).encode(), address)

        self.logger.log(message_type, f"Sent content: \"{message}\" to {receiver}")

        #continue update
        self.vp[receiver] = self.timestamps

    def receive_SES_message(self, message: Message, queue_check = False):
        self.logger.log(message.message, 0) # magic number for result

        if self.pid not in message.vp:
            self.__update_timestamps(message.timestamps)
        else:
            if is_lesser_vector(message.vp[self.pid], self.timestamps):
                #to-do implement yfs here
                if message.message_type == MessageType.READ:
                    self.receive_read(message)
                if message.message_type == MessageType.WRITE:
                    self.receive_write(message)

                self.__update_timestamps(message.timestamps)
                #update vp
                self.vp = {k: v for k, v in message.vp.items() if k != self.pid}
            else:
                self.queue.append(message)
                queue_check = True

        #check queue
        if not queue_check:
            for m in self.queue:
                self.receive_SES_message(m, True)

    def send_read(self, reciver: int):
        self.send_SES_message(reciver, "", MessageType.READ)
        print("Send read file successfully")

    def receive_read(self, message: Message):
        if self.check_yourself(message) == 1 : ## Check yourself is receiver 
            if message.message_type == MessageType.READ:    
                ## Read file request of sender
                file_content = self.read_file(self.pid)
                ## Send respond for sender
                self.send_SES_message(message.sender, file_content, -MessageType.READ)
            elif message.message_type == -MessageType.READ:
                ## sender receive respond_receiver and print content of file
                print(f"Received file from {message.sender}")
                print("Content:")
                print(message.message)

                self.write_file(message.sender, message.message)
    
    def send_write(self, recive: int, user_command: str):
        command_read = "Write File" + str(recive) + " "
        index = user_command.find(command_read)
        message = ""
        if index != -1:
            message = user_command[index + len(command_read):]
        else:
            print("Wrong commad")

        if command_read in user_command :
            print("Send read file successfully")
            self.send_SES_message(recive, message, MessageType.WRITE)
        else:
            print("Wrong commad")

    def receive_write(self, message: Message):
        if  self.check_yourself(message) == 1 : ## Check yourself is receiver 
            if message.message_type == MessageType.WRITE:
                ## need except handler here
                self.write_file(self.pid, message.message)
                message_response = "Write file successfully"
                ## Send respond for sender
                self.send_SES_message(message.sender,message_response, -MessageType.WRITE)
            elif message.message_type == - MessageType.WRITE:
                ## sender receive respond_receiver and print content of file
                print(message.message)
        elif self.check_yourself(message) == 2: ## Check yourself is guest
            print("This file is an old version")

    def serve(self):
        while True:
            # client_sock, client_addr = self.receiver.accept()

            client_request, client_address = self.receiver.recvfrom(1024)
            print(f"Connection from {client_address}")
            message = Message.from_string(client_request.decode("utf-8"))
            #to-do
            #SES
            if message.message_type >= 0:
                self.receive_SES_message(message)
            else:
                #to-do: receive message response
                if message.message_type == -MessageType.READ:
                    self.receive_read(message)
                if message.message_type == -MessageType.WRITE:
                    self.receive_write(message)
                if message.message_type == -MessageType.GET:
                    pass
                if message.message_type == -MessageType.BROADCAST:
                    pass
            #
            # if client_request == "list_files":
            #     files = os.listdir("shared_folder")
            #     file_str = "\n".join(files)
            #     client_sock.sendall(file_str.encode("utf-8"))
            # client_sock.close()
        
    def get_main_dir(self):
        try:
            return self.__main_dir
        except AttributeError:
            main_path = os.path.join(os.curdir, f"Dir{self.pid}")
            if not os.path.exists(main_path):
                os.makedirs(main_path)

            self.__main_dir = main_path
            return self.__main_dir

    def __update_timestamps(self, timestamps):
        self.timestamps[self.pid] = datetime.now().timestamp()
        for i in range(len(self.timestamps)):
            if i != self.pid:
                self.timestamps[i] = timestamps[i]

    def read_file(self, pID: int):
        file_path = os.path.join(self.__main_dir, f'Peer{pID}', f'{pID}.txt')

        try:
            with open(file_path, "r") as file:
                file_content = file.read()
                return file_content
        except FileNotFoundError:
            print("File is not exist or can not read")
        except Exception as e:
            print("Error", str(e))
    
    def write_file(self, pID: int, message: str):
        file_path = os.path.join(self.__main_dir, f'Peer{pID}', f'{pID}.txt')
        
        try:
            with open(file_path, "w") as file:
                file.write(message + "\n") 
            self.logger.log(MessageType.WRITE, "Write file successsfully.")
        except IOError:
            self.logger.log(MessageType.WRITE, "Error: Can not write file.")

    def check_yourself(self, message: Message):
        if self.pid == message.sender:
            return 0
        elif self.pid == message.receiver:
            return 1
        else:
            return 2
        
def user_interface(yfs: YFS):
    while True:
        user_commands = input("Input command: ").split()
        command = user_commands[0].lower()
        arg = int(user_commands[1][-1])

        if command == "exit":
            return
        
        if command == "write":
            if len(user_commands) > 2:
                content = user_commands[2]
                yfs.write_file(arg, content)
                #Error
                #yfs.send_write(arg, content)
                print("Send Write")
            else:
                print("Command is incorrect")

        if command == "read":
            #Error
            #yfs.send_read(arg)
            content = yfs.read_file(arg)
            print("Content:", content)
        
if __name__ == "__main__":
    print("Menu:")
    print("1. Read File + [pID]")
    print("2. Write File + [pID] + [content]")
    print("3. Exit")

    pid = int(sys.argv[1])
    num_of_proccess = int(sys.argv[2])
    server = YFS(pid, num_of_proccess)
    
    server_thread = threading.Thread(target=server.serve)
    user_interface_thread = threading.Thread(target=user_interface, args=(server,))

    server_thread.start()
    user_interface_thread.start()