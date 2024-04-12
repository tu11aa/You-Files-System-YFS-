import os
from subprocess import check_call
import uuid
import socket
from datetime import datetime
from message import Message
import os
import math
import sys

def is_lesser_vector(vector1, vector2):

    # Tính độ dài của hai vector
    length_vector1 = math.sqrt(sum([x ** 2 for x in vector1]))
    length_vector2 = math.sqrt(sum([x ** 2 for x in vector2]))

    # So sánh độ dài của hai vector
    return length_vector1 <= length_vector2

class YFS:
    HOST = '0.0.0.0'
    PORT = 8080

    def __init__(self, pid: int, num_of_peer: int) -> None:
        self.pid = pid
        self.num_of_peer = num_of_peer
        self.peer_list = {}
        self.vp = {}
        self.timestamps = [datetime.now().timestamp()] * num_of_peer
        self.queue = []
        self.__main_dir = self.get_main_dir()

        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.receiver.bind((YFS.HOST, YFS.PORT))
        self.receiver.listen(5)

    def send_SES_message(self, receiver: int, message: str, message_type: int):
        #Update self
        self.timestamps[self.pid] = datetime.now().timestamp()

        #to-do: send message to receiver
        message = Message(self.pid, receiver, message, self.timestamps, self.vp, message_type)

        #continue update
        self.vp[receiver] = self.timestamps

    def receive_SES_message(self, message: Message, queue_check = False):
        if self.pid not in message.vp:
            self.__update_timestamps(message.timestamps)
        else:
            if is_lesser_vector(message.vp[self.pid], self.timestamps):
                #to-do implement yfs here


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

    def send_read(self, recive: int, message: str):
       command_read = "Read File"

       if command_read in message :
           print("Send read file successfully")
           self.send_SES_message(recive, message, Message.READ)
       else:
           print("Wrong commad")

        
    def receive_read(self, message: Message):
        ## Read file request of sender
        content_file = self.read_file(message.receiver)
        if  self.check_yourself(message) == 1 : ## Check yourself is receiver 
            if message.message_type == Message.READ:
                ## Send respond for sender
                self.send_SES_message(message.sender, content_file, -Message.READ)
            elif message.message_type == - Message.READ:
                ## sender receive respond_receiver and print content of file
                print(message.message)
    

    def serve(self):
        while True:
            client_sock, client_addr = self.receiver.accept()
            print(f"Connection from {client_addr}")

            client_request = client_sock.recv(1024).decode("utf-8")
            message = Message.from_string(client_request)
            #to-do
            #SES
            if message.message_type == Message.READ: #or message.message_type == Message.WRITE:
                if self.pid == message.sender:
                    print("Process ", self.pid , " is sender")
                elif self.pid == message.receiver:
                    print("Process ", self.pid , "is receiver")
                    self.receive_SES_message(message)
                else:
                    print("Process ", self.pid , "is guest")
            elif message.message_type == -Message.READ:
                #to-do: receive message response
                pass
            #
            if client_request == "list_files":
                files = os.listdir("shared_folder")
                file_str = "\n".join(files)
                client_sock.sendall(file_str.encode("utf-8"))
            client_sock.close()
        
    def get_mac_address(self):
        try:
            return self.__mac_address
        except AttributeError:
            self.__mac_address = (':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1]))
            return self.__mac_address
        
    def get_main_dir(self):
        try:
            return self.__main_dir
        except AttributeError:
            storage_path = os.path.join(os.curdir, f"Dir{self.pid}")
            if not os.path.exists(storage_path):
                os.makedirs(storage_path)

            self.__main_dir = os.path.join(storage_path, self.get_mac_address())
            return self.__main_dir

    def __update_timestamps(self, timestamps):
        self.timestamps[self.pid] = datetime.now().timestamp()
        for i in range(len(self.timestamps)):
            if i != self.pid:
                self.timestamps[i] = timestamps[i]

    def read_file(pID: int):
            base_path = r"C:\Users\ThisPC\Desktop\You-Files-System-YFS-"
            relative_path = r"\\yfs\\Dir{}\\Peer{}\\{}.txt".format(pID, pID, pID)
            file_path = base_path + relative_path

            try:
                with open(file_path, "r") as file:
                    content_file = file.read()
                    print(content_file)
            except FileNotFoundError:
                print("File is exist or cant read")
            except Exception as e:
                print("Error", str(e))

    def check_yourself(self, message: Message):
        if self.pid == message.sender:
            return 0
        elif self.pid == message.receiver:
            return 1
        else:
            return 2
        
if __name__ == "__main__":
    pid = sys.argv[1]
    num_of_proccess = sys.argv[2]
    server = YFS(pid, num_of_proccess)
    server.serve()