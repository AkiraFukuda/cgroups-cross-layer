python noise.py n1 8192 90 900 4 11 28 0 >log/ex3b-n1.log 2>&1 &
python noise.py n2 2048 60 900 4 11 28 0 >log/ex3b-n2.log 2>&1 &
python noise.py n3 4096 60 900 3 11 58 0 >log/ex3b-n3.log 2>&1 &
python app.py a1 512 15 900 11 28 0 > log/ex3b-app.log 2>&1 &
