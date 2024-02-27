python noise.py n1 8192 90 1800 4 now >log/ex1a-n1.log 2>&1 &
python noise.py n2 2048 60 1800 4 now >log/ex1a-n2.log 2>&1 &
python noise.py n3 4096 60 1800 4 now >log/ex1a-n3.log 2>&1 &
python app.py a1 512 15 1800 now > log/ex1a-app.log 2>&1 &
