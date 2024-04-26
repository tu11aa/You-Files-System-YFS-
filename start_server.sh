cd yfs
if [ $DEBUG == 0]
then
    python3 yfs_user_interface.py $PID
else
    python3 test_yfs.py $PID
fi