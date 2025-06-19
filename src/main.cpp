/*
 * Copyright (c) 2017 Linaro Limited
 *
 * SPDX-License-Identifier: Apache-2.0
 */


#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/__assert.h>
#include <string.h>


#include <zephyr/devicetree.h>
#include <zephyr/drivers/adc.h>
#include <zephyr/sys/util.h>


#include "Led.hpp"
#include "SensorsMatrix.h"

/* size of stack area used by each thread */
#define STACKSIZE 1024

/* scheduling priority used by each thread */
#define PRIORITY 7

#define LED0_NODE DT_ALIAS(led0)

#if !DT_NODE_HAS_STATUS(LED0_NODE, okay)
#error "Unsupported board: led0 devicetree alias is not defined"
#endif


#if !DT_NODE_EXISTS(DT_PATH(zephyr_user)) || \
	!DT_NODE_HAS_PROP(DT_PATH(zephyr_user), io_channels) || \
	!DT_NODE_HAS_PROP(DT_PATH(zephyr_user), mux_gpios)
#error "Unsupported board: zephyr_user devicetree alias is not defined"
#endif

#define DT_SPEC_AND_COMMA(node_id, prop, idx) \
	ADC_DT_SPEC_GET_BY_IDX(node_id, idx),

/* Data of ADC io-channels specified in devicetree. */
static const struct adc_dt_spec adc_channels[] = {
	DT_FOREACH_PROP_ELEM(DT_PATH(zephyr_user), io_channels,
			     DT_SPEC_AND_COMMA)
};

#define DT_GPIO_SPEC_AND_COMMA(node_id, prop, idx) \
	GPIO_DT_SPEC_GET_BY_IDX(node_id, prop, idx),


static const struct gpio_dt_spec gpios_mux[] = {
	DT_FOREACH_PROP_ELEM(DT_PATH(zephyr_user), mux_gpios,
			     DT_GPIO_SPEC_AND_COMMA)
};

void alive(void)
{
	Led aLed( GPIO_DT_SPEC_GET_OR(LED0_NODE, gpios, {0}) );

	if ( aLed.initialize() != 0 ) {
		return;
	}

	while (1) {
		aLed.toogle();

		k_msleep(1000);
	}
}

K_THREAD_DEFINE(alive_id, STACKSIZE, alive, NULL, NULL, NULL, PRIORITY, 0, 0);

int main(void)
{
	if (ARRAY_SIZE(adc_channels) != 4)
	{
		printk("Error: Expected 4 elements in adc_channels\n");
		return -1;
	}

	if (ARRAY_SIZE(gpios_mux) != 4)
	{
		printk("Error: Expected 4 elements in gpios_mux\n");
		return -1;
	}

	SensorsMatrix sm(gpios_mux, adc_channels);

	if (sm.initialize() != 0) {
		printk("Error: Could not initialize sensors matrix\n");
		return -1;
	}

	while (1)
	{
		uint8_t aMatrix[8][8];
		sm.read(aMatrix);

		printk("Read all sensors:\n");
		for (int row = 0; row < 8; ++row) {
			for (int col = 0; col < 8; ++col) {
				printk("%3d ", aMatrix[row][col]);  // 3-digit width for alignment
			}
			printk("\n");
		}
		printk("\n");


		k_msleep(1000);
	}

	return 0;
}
