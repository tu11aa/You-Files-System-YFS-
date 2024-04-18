from message import MessageType
from datetime import datetime

class YFSLogger:
    def __init__(self, file_name = "log.log") -> None:
        self.log_file = file_name

    @classmethod
    def command_as_string(self, command):
        if command == MessageType.READ:
            return "READ"
        if command == MessageType.WRITE:
            return "WRITE"
        if command == MessageType.BROADCAST:
            return "BROADCAST"
        if command == MessageType.START_WRITING:
            return "START_WRITING"
        if command == MessageType.END_WRITING:
            return "END_WRITING"
        if command == MessageType.GET:
            return "GET"

    def log(self, command, result):
        timestamp = datetime.now()
        message = f"{timestamp}: [{YFSLogger.command_as_string(command)}] {result}\n"
        print(message)
        with open(self.log_file, "a") as f:
            f.write(message)