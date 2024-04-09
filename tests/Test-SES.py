import threading
import time
from queue import Queue

class Process:
    def __init__(self, pid, num_processes):
        self.pid = pid
        self.num_processes = num_processes
        self.vector_timestamp = [0] * (num_processes - 1)
        self.message_queue = Queue()
        self.lock = threading.Lock()
        self.V_P = {}

    def send_message(self, destination_pid, message):
        with self.lock:
            self.vector_timestamp[destination_pid - 1] += 1
            self.V_P[destination_pid] = tuple(self.vector_timestamp[:])
            self.message_queue.put((destination_pid, message, self.vector_timestamp[:]))

    def receive_message(self, sender_pid, message, sender_vector_timestamp):
        with self.lock:
            for i in range(len(self.vector_timestamp)):
                self.vector_timestamp[i] = max(self.vector_timestamp[i], sender_vector_timestamp[i])
            print(f"Process {self.pid} received message from Process {sender_pid}: {message}, Vector Timestamp: {self.vector_timestamp}")

             # In ra vector V_P của process
            print(f"Vector V_P{self.pid}: {self.V_P}")

class SESAlgorithm:
    def __init__(self, num_processes):
        self.num_processes = num_processes
        self.processes = [Process(pid, num_processes) for pid in range(1, num_processes + 1)]
        self.buffers = [[] for _ in range(num_processes)]

    def send_message(self, sender_pid, destination_pid, message):
        self.processes[sender_pid - 1].send_message(destination_pid, message)

    def deliver_messages(self):
        for process in self.processes:
            while not process.message_queue.empty():
                destination_pid, message, vector_timestamp = process.message_queue.get()
                if vector_timestamp[destination_pid - 1] <= process.vector_timestamp[destination_pid - 1]:
                    process.receive_message(destination_pid, message, vector_timestamp)
                else:
                    self.buffers[destination_pid - 1].append((destination_pid, message, vector_timestamp))

    def update_buffers(self, pid):
        for message in self.buffers[pid - 1]:
            destination_pid, msg, vector_timestamp = message
            if vector_timestamp[destination_pid - 1] <= self.processes[pid - 1].vector_timestamp[destination_pid - 1]:
                self.processes[pid - 1].receive_message(destination_pid, msg, vector_timestamp)
                self.buffers[pid - 1].remove(message)

if __name__ == "__main__":
    num_processes = 3
    ses_algo = SESAlgorithm(num_processes)

    def simulate_process(process):
        for i in range(3):
            time.sleep(1)
            destination_pid = (process.pid + 1) % num_processes + 1
            ses_algo.send_message(process.pid, destination_pid, f"Message {i+1}")
            ses_algo.deliver_messages()
            ses_algo.update_buffers(process.pid)

    threads = []
    for process in ses_algo.processes:
        t = threading.Thread(target=simulate_process, args=(process,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
