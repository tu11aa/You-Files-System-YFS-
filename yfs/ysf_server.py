import os
import uuid
import socket
from datetime import datetime
from message import Message
import math

def compare_vectors(vector1, vector2):
    # Kiểm tra số chiều của hai vector
    if len(vector1) != len(vector2):
        raise ValueError("Hai vector phải có số chiều bằng nhau")

    # Tính độ dài của hai vector
    length_vector1 = math.sqrt(sum([x ** 2 for x in vector1]))
    length_vector2 = math.sqrt(sum([x ** 2 for x in vector2]))

    # So sánh độ dài của hai vector
    return length_vector1 > length_vector2

class YFS:
    HOST = '0.0.0.0'
    PORT = 8080

    def __init__(self, pid: int, num_of_peer: int) -> None:
        self.pid = pid
        self.num_of_peer = num_of_peer
        self.peer_list = {}
        self.vp = {}
        self.timestamps = [datetime.now().timestamp()] * num_of_peer
        print(self.timestamps)
        self.__main_dir = self.get_main_dir()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((YFS.HOST, YFS.PORT))
        self.sock.listen(5)

    def serve(self):
        while True:
            client_sock, client_addr = self.sock.accept()
            print(f"Connection from {client_addr}")

            client_request = client_sock.recv(1024).decode("utf-8")
            message = Message.from_string(client_request)
            #to-do
            #SES
            if self.pid == message.sender:
                print("Process ", self.pid , " is sender")
                self.vp[message.receiver] = message.timestamps
                self.timestamps[self.pid] += 1

            elif self.pid == message.receiver:
                print("Process ", self.pid , "is receiver")
                if self.pid in message.vp:
                    self.vp = {k: v for k, v in message.vp if k != self.pid}
                else:
                    self.vp = message.vp.copy()
            else:
                print("Process ", self.pid , "is guest")
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

if __name__ == "__main__":
    server = YFS(1,5)
    server.serve()
    # print(server.get_mac_address())