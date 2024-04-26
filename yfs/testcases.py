from message import MessageType
import random

class TestCase:
    def __init__(self, type, file, content = "") -> None:
        self.type = type
        self.file = file
        self.content = content

    def is_read(self):
        return self.type == MessageType.READ
    
    def is_write(self):
        return self.type == MessageType.WRITE
    
def generate_testcases():
    testcases = []
    read_num = 18
    write_num = 12

    for i in range(read_num + write_num):
        if read_num <= 0:
            type = MessageType.WRITE
        elif write_num <= 0:
            type = MessageType.READ
        else:
            type = random.randint(4, 5)
            if type == MessageType.READ:
                read_num -= 1
            else:
                write_num -= 1
        file = f"File{random.randint(1, 5)}.txt"
        content = str(random.random())
        testcases.append(TestCase(type, file, content))

    return testcases

testcases = generate_testcases()