


#pragma once

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/__assert.h>
#include <string.h>


#include <zephyr/devicetree.h>
#include <zephyr/drivers/adc.h>
#include <zephyr/sys/util.h>


class Led
{
public:
	Led(struct gpio_dt_spec aSpec);

	int initialize();

	int toogle();

private:

	struct gpio_dt_spec spec_;
	int cnt = 0;
};
