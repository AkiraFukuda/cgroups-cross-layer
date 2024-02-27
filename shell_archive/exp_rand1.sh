python randnoise.py n1 8192 300 7200 now >log/ex4c-n1.log 2>&1 &
python randnoise.py n2 2048 200 7200 now >log/ex4c-n2.log 2>&1 &
python randnoise.py n3 4096 200 7200 now >log/ex4c-n3.log 2>&1 &
python app.py a1 256 10 1800 now
