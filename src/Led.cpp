#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/sys/printk.h>

#include "Led.hpp"

Led::Led(struct gpio_dt_spec aSpec) : spec_(aSpec)
{
}

int Led::initialize()
{
	int ret = -1;

	if (!device_is_ready(spec_.port)) {
		printk("Led::initialize() Error: %s device is not ready\n", spec_.port->name);
		return ret;
	}

	ret = gpio_pin_configure_dt(&spec_, GPIO_OUTPUT);
	if (ret != 0) {
		printk("Led::initialize() Error %d: failed to configure pin %d\n", ret, spec_.pin);
		return ret;
	}

	return 0;
}

int Led::toogle()
{
	cnt++;
	return gpio_pin_set(spec_.port, spec_.pin, cnt % 2);
}
