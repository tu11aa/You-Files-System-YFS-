import json

class MessageType:
    #use negative one for response
    BROADCAST = 1
    GET = 2
    READ = 4
    WRITE = 5
    START_WRITING = 6
    END_WRITING = 7


class Message:
    @classmethod
    def from_dict(cls, message):
        return Message(
            message["sender"],
            message["receiver"],
            message["message"],
            message["timestamps"],
            message["vp"],
            message["message_type"],
        )
    
    @classmethod
    def from_string(cls, message):
        return Message.from_dict(json.loads(message))

    def __init__(self, sender: int, receiver: int, message: str, timestamps: list, vp: dict, message_type: int) -> None:
        self.sender = sender
        self.receiver = receiver
        self.message = message
        self.timestamps = timestamps
        self.vp = vp
        self.message_type = message_type

    def __str__(self) -> str:
        return json.dumps(self.__dict__)