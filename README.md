# You-Files-System-YFS-
A network file sharing protocol that defines the way files are stored and retrieved from storage devices across networks

# Prerequisites
- Docker with Compose version 3
- Python 3

# How to run
Create .env file at root folder

## With user interface
1. Add DEBUG=0 to .env
2. Set dockerfile in compose.yaml to 
    dockerfile: Dockerfile_user
2. Run make_all_user.bat
3. In each termial opend, run ./start_server.sh to run yfs server
4. Input commands

## AUTORUN WITHOUT DEBUG OPTION (Less logs)
1. Add DEBUG=0 to .env
2. Run make_all.bat
3. See logs in ./Logs and files in ./Dirs

## AUTORUN WITH DEBUG OPTION (Detailed logs)
1. Add DEBUG=1 to .env
2. Run make_all.bat
3. See logs in ./Logs and files in ./Dirs