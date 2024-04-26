if [ $UI -eq 0 ]; then
    cd yfs
    python3 test_yfs.py $PID
else
    sleep infinity
fi