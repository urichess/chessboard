#INIT ENV
export ZEPHYR_BASE=~/zephyrproject/zephyr
source ~/zephyrproject/.venv/bin/activate

#COMPILE

west build -p always -b arduino_uno_r4_wifi
west build -p always -b arduino_uno_r4_wifi -t devicetree

west build -p always -b nucleo_g474re
west build -p always -b nucleo_g474re -t devicetree

#CONFIG

west build -b arduino_uno_r4_wifi -t menuconfig

#UTILS
west boards


#UPGRADING

cd  $ZEPHYR_BASE
git pull
west update
west packages pip --install

