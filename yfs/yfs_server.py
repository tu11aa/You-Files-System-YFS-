import os
import socket
from datetime import datetime
import math

from message import Message, MessageType
from yfs_logger import YFSLogger

def is_lesser_vector(vector1, vector2):
    sorted_v1 = dict(sorted(vector1.items()))
    sorted_v2 = dict(sorted(vector2.items()))
    # Tính độ dài của hai vector
    length_vector1 = math.sqrt(sum([x ** 2 for x in sorted_v1.values()]))
    length_vector2 = math.sqrt(sum([x ** 2 for x in sorted_v2.values()]))

    # So sánh độ dài của hai vector
    return length_vector1 <= length_vector2

class YFS:
    HOST = '0.0.0.0'
    PORT = 8080

    def __init__(self, pid: int) -> None:
        self.pid = pid
        self.peer_to_address = {}
        self.vp = {}
        self.timestamps = {self.pid:datetime.now()}
        self.queue = []
        self.__main_dir = self.get_main_dir()
        self.logger = YFSLogger()

        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receiver.bind((YFS.HOST, YFS.PORT))
        # self.receiver.listen(5)

        self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def read(self, filename):
        pid = int(filename[4:].replace(".txt", ""))
        if pid == self.pid:
            self.read_file(pid)
        else:
            self.send_read(pid)

    def write(self, filename, message):
        pid = int(filename[4:].replace(".txt", ""))
        if pid == self.pid:
            self.write_file(pid, message)
            self.send_end_write(self.pid)
        else:
            self.send_write(pid, message)

    def send_SES_message(self, receiver: int, message: str, message_type: int):
        #Update self
        self.timestamps[self.pid] = datetime.now().timestamp()

        #to-do: send message to receiver
        message = Message(self.pid, receiver, message, self.timestamps, self.vp, message_type)
        if (message_type == MessageType.BROADCAST):
            address = ('<broadcast>', YFS.PORT)
            self.logger.log(message_type, f"Sent broadcast message")
        else:
            address = (self.peer_to_address[receiver], YFS.PORT)
        self.sender.sendto(str(message).encode(), address)
        self.logger.log(message_type, f"Sent to {receiver} successfully")

        #continue update
        self.vp[receiver] = self.timestamps

    def receive_SES_message(self, message: Message, address, queue_check = False):
        # self.logger.log(message.message_type, 0) # magic number for result

        if self.pid not in message.vp:
            self.__update_timestamps(message.timestamps)
        else:
            if is_lesser_vector(message.vp[self.pid], self.timestamps):
                if message.message_type >= 0:
                    if message.message_type == MessageType.BROADCAST:
                        self.receive_broadcast(message, address)
                    elif message.message_type == MessageType.READ:
                        self.receive_read(message)
                    elif message.message_type == MessageType.WRITE:
                        self.receive_write(message)
                else:
                    if message.message_type == -MessageType.BROADCAST:
                        self.receive_broadcast(message, address)
                    elif message.message_type == -MessageType.READ:
                        self.receive_read(message)
                    elif message.message_type == -MessageType.WRITE:
                        self.receive_write(message)
                    elif message.message_type == -MessageType.MOUNT:
                        pass

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

    def send_broadcast(self):
        self.send_SES_message(-1, "", MessageType.BROADCAST)

    def receive_broadcast(self, message: Message, address):
        self.logger.log(message.message_type, f"Received from {message.sender}")
        if self.__check_yourself(message) != 0:
            self.peer_to_address[message.sender] = address
            self.timestamps[message.sender] = datetime.now()
            if message.message_type == MessageType.BROADCAST:
                self.send_SES_message(message.sender, "", -MessageType.BROADCAST)
            elif message.message_type == -MessageType.BROADCAST:
                self.send_mount(message.sender)

    def send_mount(self, reciver: int):
        self.send_SES_message(reciver, "", MessageType.MOUNT)

    def receive_mount(self, message: Message):
        if self.__check_yourself(message) == 1 : ## Check yourself is receiver 
            if message.message_type == MessageType.READ:    
                ## Read file request of sender
                file_content = self.read_file(self.pid)
                ## Send respond for sender
                self.send_SES_message(message.sender, file_content, -MessageType.MOUNT)
            elif message.message_type == -MessageType.MOUNT:
                ## sender receive respond_receiver and print content of file
                self.logger.log(-MessageType.MOUNT, f"Received file from {message.sender}")
                peer_path = os.path.join(self.__main_dir, f"Peer{message.sender}")
                if not os.path.exists(peer_path):
                    os.mkdir(peer_path)
                self.write_file(message.sender, message.message)

    def send_read(self, receiver: int):
        self.send_SES_message(receiver, "", MessageType.READ)

    def receive_read(self, message: Message):
        if self.__check_yourself(message) == 1 : ## Check yourself is receiver 
            if message.message_type == MessageType.READ:    
                ## Read file request of sender
                file_content = self.read_file(self.pid)
                ## Send respond for sender
                self.send_SES_message(message.sender, file_content, -MessageType.READ)
            elif message.message_type == -MessageType.READ:
                ## sender receive respond_receiver and print content of file
                self.logger.log(-MessageType.READ, f"Received file from {message.sender}")
                self.logger.log(MessageType.READ, "Content:")
                self.logger.log(MessageType.READ, message.message)

                self.write_file(message.sender, message.message)
    
    def send_write(self, reciver: int, message: str):  
        self.send_start_write()
        self.send_SES_message(reciver, message, MessageType.WRITE)

    def receive_write(self, message: Message):
        if  self.__check_yourself(message) == 1 : ## Check yourself is receiver 
            if message.message_type == MessageType.WRITE:
                ## need except handler here
                self.write_file(self.pid, message.message)
                message_response = "Write file successfully"
                ## Send respond for sender
                self.send_SES_message(message.sender,message_response, -MessageType.WRITE)
                self.send_end_write(message.sender)
            elif message.message_type == -MessageType.WRITE:
                ## sender receive respond_receiver and print content of file
                self.logger.log(-MessageType.WRITE, message.message)

    def send_start_write(self):
        # send list peer_to_address - sender.
        message = "Start Writing"
        for i in self.peer_to_address:
            self.send_SES_message(i, message, MessageType.START_WRITING)
    
    def receive_start_write(self, message: Message):
        if self.__check_yourself(message) == 2: #check yourself is guest
            if message.message_type == MessageType.START_WRITING:
                self.logger.log(message.message_type,"This file is an old version")

    def send_end_write(self, exclude: int):
        # send list peer_to_address - sender.
        message = "End Write"
        for i in self.peer_to_address:
            if i != exclude:
                self.send_SES_message(i, message, MessageType.END_WRITING)

    def receive_end_write(self, message: Message):
        if self.__check_yourself(message) == 2 : #check yourself is guest 
            if message.message_type == MessageType.END_WRITING:
                self.send_read(message.sender)
                self.logger.log(message.message_type, "Write file done")

    def serve(self):
        while True:
            # client_sock, client_addr = self.receiver.accept()

            client_request, client_address = self.receiver.recvfrom(1024)
            message = Message.from_string(client_request.decode("utf-8"))
            
            self.receive_SES_message(message, client_address)
        
    def get_main_dir(self):
        try:
            return self.__main_dir
        except AttributeError:
            main_path = os.path.join(os.curdir, f"Dir{self.pid}")
            if not os.path.exists(main_path):
                os.mkdir(main_path)
                os.mkdir(os.path.join(main_path, f"Peer{self.pid}"))

            self.__main_dir = main_path
            return self.__main_dir

    def read_file(self, pID: int):
        file_path = os.path.join(self.__main_dir, f'Peer{pID}', f'File{pID}.txt')

        try:
            with open(file_path, "r") as file:
                file_content = file.read()
                return file_content
        except FileNotFoundError:
            self.logger.log(MessageType.READ, "File is not exist or can not read")
        except Exception as e:
            self.logger.log(MessageType.READ, f"Got error {str(e)}")
    
    def write_file(self, pID: int, message: str):
        file_path = os.path.join(self.__main_dir, f'Peer{pID}', f'File{pID}.txt')
        
        try:
            with open(file_path, "w") as file:
                file.write(message + "\n") 
            self.logger.log(MessageType.WRITE, f"Write {message} to {file_path} successsfully.")
        except IOError:
            self.logger.log(MessageType.WRITE, f"Error: Can not write to {file_path}.")

    def __update_timestamps(self, timestamps):
        self.timestamps[self.pid] = datetime.now().timestamp()
        for pid in self.timestamps:
            if pid != self.pid:
                self.timestamps[pid] = timestamps[pid]

    def __check_yourself(self, message: Message):
        if self.pid == message.sender:
            return 0
        elif self.pid == message.receiver:
            return 1
        else:
            return 2