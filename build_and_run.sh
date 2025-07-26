#!/bin/bash
rm -rf build
mkdir build
cd build
cmake -G Ninja ..
ninja
# chmod +x ./../run.sh
# sudo ./../run.sh
cp main_app ../main_app
chmod +x ../main_app
cd ..
sudo python3 demo.py