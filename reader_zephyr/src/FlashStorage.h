#ifndef __FLASH_STORAGE_H__
#define __FLASH_STORAGE_H__

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/__assert.h>
#include <string.h>

struct storage_data {
    uint32_t magic = 0;
    uint32_t calibrations[8][8] = {0};
    uint32_t crc = 0;
};

class FlashStorage {
public:

	explicit FlashStorage() {}

	int initialize();

	int read(storage_data & data);

	int write(storage_data & data);

	/*

	read();

	write();

	isEmpty();

	 */
protected:
};

#endif
