
#include "FlashStorage.h"

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/flash.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/__assert.h>
#include <zephyr/sys/crc.h>
#include <string.h>

#define CALIB_MAGIC 0xCAFEBABE
#define FLASH_SECTOR_SIZE 4096         // Tamaño típico de sector
#define NUM_VALUES 70


//#define FLASH_NODE DT_NODELABEL(flash_storage) 
#define FLASH_NODE DT_CHOSEN(config_data)

#define FLASH_STORAGE_ADDRESS DT_REG_ADDR(FLASH_NODE)
#define FLASH_STORAGE_SIZE DT_REG_SIZE(FLASH_NODE)

BUILD_ASSERT(sizeof(struct storage_data) <= FLASH_STORAGE_SIZE, "calib_data exceeds flash partition size");


static const struct device *flash_dev;

int FlashStorage::initialize() {

	flash_dev = DEVICE_DT_GET(DT_CHOSEN(zephyr_flash_controller));
	if (!device_is_ready(flash_dev)) {
		printk("Flash device not ready!\n");
	}

	return 0;

}

int FlashStorage::read(storage_data & data) {

    int err = flash_read(flash_dev, FLASH_STORAGE_ADDRESS, &data, sizeof(data));
    if (err != 0) {
        printk("Read failed: %d\n", err);
        return err;
    }

    if (data.magic != CALIB_MAGIC) {
        printk("No valid magic number\n");
        return -EINVAL;
    }

    uint32_t crc_check = crc32_ieee((const uint8_t *)&data, sizeof(data) - sizeof(data.crc));
    if (crc_check != data.crc) {
        printk("CRC mismatch\n");
        return -EIO;
    }

    return 0;
}

int FlashStorage::write(storage_data & data) {

	    data.magic = CALIB_MAGIC;
	    data.crc = crc32_ieee((const uint8_t *)&data, sizeof(data) - sizeof(data.crc));

	    if (sizeof(data) > FLASH_STORAGE_SIZE) {
	        printk("calib_data too large for flash partition\n");
	        return -ENOMEM;
	    }

	    int err = flash_erase(flash_dev, FLASH_STORAGE_ADDRESS, FLASH_STORAGE_SIZE);
	    if (err != 0) {
	        printk("Flash erase failed: %d\n", err);
	        return err;
	    }

	    err = flash_write(flash_dev, FLASH_STORAGE_ADDRESS, &data, sizeof(data));
	    if (err != 0) {
	        printk("Flash write failed: %d\n", err);
	    }

	    return err;

	return 0;
}
