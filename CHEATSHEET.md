west build -p always -b arduino_uno_r4_wifi  samples/basic/blinky
west boards
source ~/zephyrproject/.venv/bin/activate
source ~/zephyrproject/.venv/bin/activate
export ZEPHYR_BASE=~/zephyrproject/zephyr
west "$@"
west build -b arduino_uno_r4_wifi -t menuconfig

#UPGRADING

cd  $ZEPHYR_BASE
git pull
west update
west packages pip --install
