
#include "FlashStorage.h"

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/flash.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/__assert.h>
#include <zephyr/sys/crc.h>
#include <string.h>

#define CALIB_MAGIC 0xCAFEBABE
#define FLASH_NODE DT_CHOSEN(config_data)
#define FLASH_STORAGE_ADDRESS DT_REG_ADDR(FLASH_NODE)
#define FLASH_STORAGE_SIZE DT_REG_SIZE(FLASH_NODE)

static const struct device *flash_dev = nullptr;

BUILD_ASSERT(sizeof(struct storage_data) <= FLASH_STORAGE_SIZE, "calib_data exceeds flash partition size");

int FlashStorage::initialize() {
	flash_dev = DEVICE_DT_GET(DT_CHOSEN(zephyr_flash_controller));

	if (!device_is_ready(flash_dev)) {
		printk("%s ERROR: Flash device not ready!\n", __func__);
		return -1;
	}

	return 0;
}

int FlashStorage::read(storage_data & data) {

	if (!flash_dev) {
		printk("%s ERROR: Flash device not ready!\n", __func__);
		return -1;
	}

    int err = flash_read(flash_dev, FLASH_STORAGE_ADDRESS, &data, sizeof(data));
    if (err != 0) {
        printk("%s Error: Read failed: %d\n", __func__, err);
        return err;
    }

    if (data.magic != CALIB_MAGIC) {
        printk("%s No valid magic number\n", __func__);
        return -EINVAL;
    }

    uint32_t crc_check = crc32_ieee((const uint8_t *)&data, sizeof(data) - sizeof(data.crc));
    if (crc_check != data.crc) {
        printk("%s CRC mismatch\n", __func__);
        return -EIO;
    }

    return 0;
}

int FlashStorage::write(storage_data & data) {

	if (!flash_dev) {
		printk("%s ERROR: Flash device not ready!\n", __func__);
		return -1;
	}

	data.magic = CALIB_MAGIC;
	data.crc = crc32_ieee((const uint8_t *)&data, sizeof(data) - sizeof(data.crc));

	if (sizeof(data) > FLASH_STORAGE_SIZE) {
		printk("%s calib_data too large for flash partition\n", __func__);
		return -ENOMEM;
	}

	int err = flash_erase(flash_dev, FLASH_STORAGE_ADDRESS, FLASH_STORAGE_SIZE);
	if (err != 0) {
		printk("%s Flash erase failed: %d\n", __func__, err);
		return err;
	}

	err = flash_write(flash_dev, FLASH_STORAGE_ADDRESS, &data, sizeof(data));
	if (err != 0) {
		printk("%s Flash write failed: %d\n", __func__, err);
	}

	return 0;
}
