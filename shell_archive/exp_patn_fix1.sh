python noise.py n1 6144 60 1200 5 now >log/ex0917_0-n1.log 2>&1 &
python noise.py n2 2048 30 1200 5 now >log/ex0917_0-n2.log 2>&1 &
python app.py a1 512 15 1200 now > log/ex0917_0-app.log 2>&1 &
