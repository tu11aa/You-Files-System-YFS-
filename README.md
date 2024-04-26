# You-Files-System-YFS-
A network file sharing protocol that defines the way files are stored and retrieved from storage devices across networks

# Prerequisites
- Docker with Compose version 3
- Python 3

# How to run
Create .env file at root folder
- Set DEBUG=1 at .env to get detailed logs, else set DEBUG=0

## With user interface:
1. Add UI=1 to .env
2. Run make_all_ui.bat
3. In each opened termial, run ./start_server.sh to run yfs server
4. Input commands

## Autorun without user interface:
1. Add UI=0 to .env
2. Run make_all.bat
3. See logs in ./Logs and files in ./Dirs