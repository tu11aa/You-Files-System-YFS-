import json

class Message:
    #use negative one for response
    BROADCAST = 1
    GET = 2
    READ = 4
    WRITE = 5
    START_WRITING = 6
    END_WRITING = 7
    

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
    
if __name__ == "__main__":
    #how to use :))))

    #p1:
    p1_tp = [1, 0]
    p1_vp = {}
    m1 = Message("p1", "p2", "hello", p1_tp, p1_vp, Message.BROADCAST)
    #send
    p1_vp[m1.receiver] = m1.timestamps
    print(p1_vp)
    #--------------------------------------#
    p2_tp = [0, 0]
    p2_vp = {}

    m2 = str(m1)
    m2 = Message.from_string(m2)
    #compare m2.timestamp < m1.timestamp