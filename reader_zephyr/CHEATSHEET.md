#INIT ENV
. ./scripts/activate

#COMPILE

./scripts/build_all.sh [-clean]


#ZEPHYR COMMANDS TO COMPILE

west build -p always -b arduino_uno_r4_wifi

west build -p always -b nucleo_g474re
west build -p auto -b nucleo_g474re
west build -p always -b nucleo_g474re -t dt


#CONFIG

west build -b chessboard_l431_v1 -t menuconfig app

#UTILS
west boards


#UPGRADING

cd  $ZEPHYR_BASE
git pull
west update
west packages pip --install

python -m serial.tools.miniterm /dev/ttyACM0 115200
