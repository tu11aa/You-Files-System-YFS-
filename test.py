import sys

if __name__ == "__main__":
    pid = int(sys.argv[1])
    
    while True:
        user_command = input("Input command")

        print(f"Command {user_command} from [PID {pid}]")

        if (user_command.lower() == "exit"):
            break