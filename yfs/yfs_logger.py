from message import MessageType
from datetime import datetime

class YFSLogger:
    def __init__(self, file_name = "log.log") -> None:
        self.log_file = file_name

    @classmethod
    def command_as_string(self, command):
        if command < 0:
            response = "RESPONSE_"
        else:
            response = ""
        result = ""
        if command == MessageType.READ:
            result = "READ"
        if command == MessageType.WRITE:
            result = "WRITE"
        if command == MessageType.BROADCAST:
            result = "BROADCAST"
        if command == MessageType.START_WRITING:
            result = "START_WRITING"
        if command == MessageType.END_WRITING:
            result = "END_WRITING"
        if command == MessageType.GET:
            result = "GET"
        return response + result

    def log(self, command, result):
        timestamp = datetime.now()
        message = f"{timestamp}: [{YFSLogger.command_as_string(command)}] {result}\n"
        print(message)
        with open(self.log_file, "a") as f:
            f.write(message)