import os
import uuid
import socket

class YFS:
    HOST = '0.0.0.0'
    PORT = 8080

    def __init__(self) -> None:
        self.__mac_address = self.get_mac_address()
        self.__main_dir = self.get_main_dir()
        self.peer_list = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((YFS.HOST, YFS.PORT))
        self.sock.listen(5)

    def serve(self):
        while True:
            client_sock, client_addr = self.sock.accept()
            print(f"Connection from {client_addr}")
            client_request = client_sock.recv(1024).decode("utf-8")
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
            storage_path = os.path.join(os.curdir, "Storage")
            if not os.path.exists(storage_path):
                os.makedirs(storage_path)

            self.__main_dir = os.path.join(storage_path, self.get_mac_address())
            return self.__main_dir

    
server = YFS()