from message import MessageType
from datetime import datetime

class YFSLogger:
    def __init__(self, file_name = "log.log", debugging = True) -> None:
        self.log_file = file_name
        self.debugging = debugging

    @classmethod
    def command_as_string(self, command: int):
        if command is None:
            return ""
        if command < 0:
            response = "RESPONSE_"
            command = - command
        else:
            response = ""
        result = ""
        if command == MessageType.READ:
            result = "READ"
        elif command == MessageType.WRITE:
            result = "WRITE"
        elif command == MessageType.BROADCAST:
            result = "BROADCAST"
        elif command == MessageType.START_WRITING:
            result = "START_WRITING"
        elif command == MessageType.END_WRITING:
            result = "END_WRITING"
        elif command == MessageType.MOUNT:
            result = "MOUNT"
        return response + result

    def log(self, command: int, result, other: str = "", force_stdout = False):
        timestamp = datetime.now()
        if len(other) != 0:
            message = f"{timestamp}: [{other.upper()}] {result}\n"
        else:
            message = f"{timestamp}: [{YFSLogger.command_as_string(command)}] {result}\n"
        if self.debugging or force_stdout:
            print(message)
        with open(self.log_file, "a") as f:
            f.write(message)