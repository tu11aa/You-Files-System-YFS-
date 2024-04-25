import os
import socket
from datetime import datetime
import math

from message import Message, MessageType
from yfs_logger import YFSLogger

def is_lesser_vector(vector1: dict, vector2: dict):
    sorted_v1 = dict(sorted(vector1.items(), key=lambda item: int(item[0])))
    sorted_v2 = dict(sorted(vector2.items(), key=lambda item: int(item[0])))
    # Tính độ dài của hai vector
    length_vector1 = math.sqrt(sum([x ** 2 for x in sorted_v1.values()]))
    length_vector2 = math.sqrt(sum([x ** 2 for x in sorted_v2.values()]))

    # So sánh độ dài của hai vector
    return length_vector1 <= length_vector2

time_now = 0
def now():
    # return datetime.now().timestamp()\
    global time_now
    time_now += 1
    return time_now

class YFS:
    HOST = '0.0.0.0'
    PORT = 8080

    def __init__(self, pid: str) -> None:
        self.pid = pid
        self.peer_to_address = {}
        self.vp = {}
        self.timestamps = {}
        self.queue = []
        self.__main_dir = self.get_main_dir()
        self.logger = YFSLogger(f"./Logs/log{self.pid}.log", debugging=False)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind((YFS.HOST, YFS.PORT))
        self.logger.log(None, f"YFS server PID {self.pid} started on port {YFS.PORT}")

        self.send_broadcast()

    def read(self, filename):
        pid = filename[4:].replace(".txt", "")
        if not pid.isnumeric():
            self.logger.log(MessageType.READ, f"Can not read {filename}")
            return None
        if pid == self.pid:
            return self.read_file(pid)
        else:
            # if os.path.exists(os.path.join(self.__main_dir, f"Peer{pid}", f"File{pid}.txt")):
            #     return self.read_file(pid)
            # else:
                self.send_read(pid)
                return None

    def write(self, filename, message):
        pid = filename[4:].replace(".txt", "")
        if pid == self.pid:
            self.send_start_write(f"{pid} Start writing to File{pid}", pid)
            status = self.write_file(pid, message)
            if status is not None:
                self.send_end_write(message, self.pid)
        else:
            self.send_write(pid, message)

    def send_message(self, receiver: str, message: str, message_type: int, status: bool = True):
        #Update self
        if self.__is_SES(message_type):
            self.timestamps[self.pid] = now()
            self.logger.log(message_type, f"Updated timestamp: {self.timestamps}", force_stdout=True)

        message_obj = Message(self.pid, receiver, message, self.timestamps, self.vp, message_type, status)
        if (message_type == MessageType.BROADCAST):
            address = ('<broadcast>', YFS.PORT)
        else:
            try:
                address = self.peer_to_address[receiver]
            except KeyError:
                self.logger.log(message_type, f"Not mount to YFS{receiver} yet")
                return
        self.sock.sendto(str(message_obj).encode(), address)

        if (message_type == MessageType.BROADCAST):
            self.logger.log(message_type, f"Sent broadcast message", force_stdout=True)
        else:
            self.logger.log(message_type, f"Sent to {receiver}:{address} successfully", force_stdout=True)

        #continue update
        if  self.__is_SES(message_type):
            self.vp[receiver] = self.timestamps.copy()
            self.logger.log(message_type, f"Updated vp: {self.vp}", force_stdout=True)

    def receive_message(self, message: Message, address, queue_check = False, queue_index: int = -1):
        # self.logger.log(message.message_type, 0) # magic number for result
        if message.message_type == MessageType.BROADCAST and self.__check_myself(message) == 0:
            return
        
        if self.pid not in message.vp or self.__compare_timestamps(message.vp[self.pid]):
            if queue_check:
                self.logger.log(message.message_type, "Pushed out of queue", force_stdout=True)
                self.queue.pop(queue_index)
            else:
                self.logger.log(message.message_type, f"Received from {message.sender}", force_stdout=True)

            if  self.__is_SES(message.message_type):
                self.__update_timestamps(message.timestamps)
                self.logger.log(message.message_type, f"Updated timestamp: {self.timestamps}", force_stdout=True)
                self.__update_vp(message.vp)
                self.logger.log(message.message_type, f"Updated vp: {self.vp}", force_stdout=True)

            if message.message_type >= 0:
                if message.message_type == MessageType.BROADCAST:
                    self.receive_broadcast(message, address)
                elif message.message_type == MessageType.READ:
                    self.receive_read(message)
                elif message.message_type == MessageType.WRITE:
                    self.receive_write(message)
                elif message.message_type == MessageType.END_WRITING:
                    self.receive_end_write(message)
                elif message.message_type == MessageType.START_WRITING:
                    self.receive_start_write(message)
                elif message.message_type == MessageType.MOUNT:
                    self.receive_mount(message, address)
            else:
                if message.message_type == -MessageType.READ:
                    self.receive_read(message)
                elif message.message_type == -MessageType.WRITE:
                    self.receive_write(message)
                elif message.message_type == -MessageType.MOUNT:
                    self.receive_mount(message)

        elif not queue_check:
            self.logger.log(message.message_type, f"Added message from {message.sender} to QUEUE", force_stdout=True)
            self.queue.append(message)
            queue_check = True

        #check queue
        if not queue_check:
            for i, m in enumerate(self.queue):
                self.receive_message(m, address, queue_check = True, queue_index = i)

    def send_broadcast(self):
        self.send_message(-1, "", MessageType.BROADCAST)

    def receive_broadcast(self, message: Message, address):
        if self.__check_myself(message) != 0:
            self.peer_to_address[message.sender] = address
            if message.message_type == MessageType.BROADCAST:
                self.send_mount(message.sender)

    def send_mount(self, receiver: str):
        file_content = self.read_file(self.pid)
        if file_content != None:
            self.send_message(receiver, file_content, MessageType.MOUNT)
        else:
            self.send_message(receiver, f"File{self.pid} is not exist or can not read", MessageType.MOUNT, False)

    def receive_mount(self, message: Message, address = None):
        if self.__check_myself(message) == 1 : ## Check yourself is receiver 
            def update_folder():
                #Create Dir if not exists
                self.logger.log(MessageType.MOUNT, f"Received folder Peer{message.sender} from {message.sender}", force_stdout=True)
                peer_path = os.path.join(self.__main_dir, f"Peer{message.sender}")
                if not os.path.exists(peer_path):
                    try:
                        os.mkdir(peer_path)
                    except:
                        self.logger.log(0, f"Can not create {peer_path}", other="Error")
                #write file
                if message.status:
                    self.write_file(message.sender, message.message)
                else:
                    self.logger.log(0, message.message, other="INFO")

            if message.message_type == MessageType.MOUNT:
                self.peer_to_address[message.sender] = address
                update_folder()
                ## Read file request of sender
                file_content = self.read_file(self.pid)
                ## Send respond for sender
                if file_content is None:
                    self.send_message(message.sender, f"File{self.pid} is not exist or can not read", -MessageType.MOUNT, status=False)
                else:
                    self.send_message(message.sender, file_content, -MessageType.MOUNT)
            elif message.message_type == -MessageType.MOUNT:
                ## sender receive respond_receiver and print content of file
                update_folder()

    def send_read(self, receiver: str):
        self.send_message(receiver, "", MessageType.READ)

    def receive_read(self, message: Message):
        if self.__check_myself(message) == 1 : ## Check yourself is receiver 
            if message.message_type == MessageType.READ:    
                ## Read file request of sender
                file_content = self.read_file(self.pid)
                ## Send respond for sender
                if file_content is None:
                    self.send_message(message.sender, f"File{self.pid} is not exist or can not read", -MessageType.READ, status=False)
                else:
                    self.send_message(message.sender, file_content, -MessageType.READ)
            elif message.message_type == -MessageType.READ:
                ## sender receive respond_receiver and print content of file
                if not message.status:
                    self.logger.log(-MessageType.READ, f"Got error '{message.message}' while reading File{message.sender}", force_stdout=True)
                else:
                    self.write_file(message.sender, message.message)

                    self.logger.log(-MessageType.READ, f"Received 'File{message.sender}' from {message.sender}", force_stdout=True)
                    self.logger.log(-MessageType.READ, "Content:", force_stdout=True)
                    self.logger.log(-MessageType.READ, message.message, force_stdout= True)
    
    def send_write(self, reciver: str, message: str):  
        self.send_message(reciver, message, MessageType.WRITE)

    def receive_write(self, message: Message):
        if self.__check_myself(message) == 1 : ## Check yourself is receiver 
            if message.message_type == MessageType.WRITE:
                self.send_start_write(f"{message.sender} Start writing to File{self.pid}", exclude=message.sender)
                status = self.write_file(self.pid, message.message)
                if status:
                    self.send_message(message.sender, message.message, -MessageType.WRITE)
                    self.send_end_write(message.message, exclude=message.sender)
                else:
                    self.send_message(message.sender, self.read_file(self.pid), -MessageType.WRITE, status=False)
                    self.send_end_write(f"Fail to write {message.message} to File{self.pid}", message.sender, status=False)
            elif message.message_type == -MessageType.WRITE:
                ## sender receive respond_receiver and print content of file
                if message.status:
                    self.write_file(message.sender, message.message)
                else:
                    self.logger.log(-MessageType.WRITE, f"Can not write to File{message.sender}. Reverted!", force_stdout=True)

    def send_start_write(self, message: str, exclude: str):
        # send list peer_to_address - sender.
        for i in self.peer_to_address:
            if i != self.pid and i != exclude:
                self.send_message(i, message, MessageType.START_WRITING)
    
    def receive_start_write(self, message: Message):
        if self.__check_myself(message) == 1: #check yourself is receiver
            if message.message_type == MessageType.START_WRITING:
                self.logger.log(message.message_type, message.message, force_stdout=True)

    def send_end_write(self, message: str, exclude: str, status = True):
        for i in self.peer_to_address:
            if i !=self.pid and i != exclude:
                self.send_message(i, message, MessageType.END_WRITING, status)

    def receive_end_write(self, message: Message):
        if self.__check_myself(message) == 1 :
            if message.message_type == MessageType.END_WRITING:
                if message.status:
                    self.logger.log(message.message_type, f"File{message.sender} is old, updating ...", force_stdout=True)
                    self.write_file(message.sender, message.message)
                else:
                    self.logger.log(message.message_type, message.message, force_stdout=True)
                

    def serve(self):
        self.logger.log(-1, "Start YFS server", "SERVE", force_stdout=True)
        while True:
            client_request, client_address = self.sock.recvfrom(1024)
            message = Message.from_string(client_request.decode())
            
            self.receive_message(message, client_address)
            # t = threading.Thread(target=self.receive_SES_message, args=(message, client_address,))
            # t.start()
        
    def get_main_dir(self):
        try:
            return self.__main_dir
        except AttributeError:
            main_path = os.path.join(os.curdir, f"Dir{self.pid}")
            peer_path = os.path.join(main_path, f"Peer{self.pid}")
            if not os.path.exists(main_path):
                os.mkdir(main_path)
            if not os.path.exists(peer_path):
                os.mkdir(peer_path)

            self.__main_dir = main_path
            return self.__main_dir

    def read_file(self, pID: str):
        file_path = os.path.join(self.__main_dir, f'Peer{pID}', f'File{pID}.txt')

        try:
            with open(file_path, "r") as file:          
                file_content = file.read()
                return file_content
        except FileNotFoundError:
            self.logger.log(0, f"File{pID} is not exist or can not read", other="READFILE", force_stdout=True)
            return None
    
    def write_file(self, pID: int, message: str):
        file_path = os.path.join(self.__main_dir, f'Peer{pID}', f'File{pID}.txt')
        
        try:
            with open(file_path, "w") as file:
                file.write(message + "\n") 
            self.logger.log(0, f"Wrote {message} to {file_path} successsfully.", other="WRITEFILE", force_stdout=True)
            return message
        except IOError:
            self.logger.log(0, f"Error: Can not write to {file_path}.", other="WRITEFILE", force_stdout=True)
            return None

    def __update_timestamps(self, timestamps):
        self.logger.log(-1, f"{timestamps}", "OTHER TIMESTAMP")
        self.timestamps[self.pid] = now()
        for pid in timestamps:
            if pid != self.pid:
                self.timestamps[pid] = timestamps[pid]

    def __update_vp(self, vp):
        self.logger.log(-1, f"{vp}", "OTHER VP")
        for pid in vp:
            if pid != self.pid:
                if pid not in self.vp:
                    self.vp[pid] = vp[pid].copy()
                else:
                    for _pid in vp[pid]:
                        if _pid in self.vp[pid]:
                            if self.vp[pid][_pid] < vp[pid][_pid]:
                                self.vp[pid][_pid] = vp[pid][_pid]
                        else:
                            self.vp[pid][_pid] = vp[pid][_pid]

    def __compare_timestamps(self, timestamps: dict):
        for timestamp, value in timestamps.items():
            if timestamp not in self.timestamps:
                return False
            if self.timestamps[timestamp] < value:
                return False
        return True

    def __check_myself(self, message: Message):
        if self.pid == message.sender:
            return 0
        elif self.pid == message.receiver:
            return 1
        else:
            return 2
        
    def __is_SES(self, message_type):
        return abs(message_type) == MessageType.READ or abs(message_type) == MessageType.WRITE 