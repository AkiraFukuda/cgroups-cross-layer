python noise.py n1 6144 60 1200 5 4 49 0 >log/ex0912n_40-n1.log 2>&1 &
python noise.py n2 2048 30 1200 5 4 49 0 >log/ex0912n_40-n2.log 2>&1 &
python noise.py n3 4096 30 1200 4 5 29 0 >log/ex0912n_40-n2n.log 2>&1 &
python app.py a1 512 128 1200 19 9 0 > log/ex0912n_40-app.log 2>&1 &

