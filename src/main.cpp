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


void matrix(void)
{
	SensorsMatrix sm;

	if (sm.initialize() != 0) {
		printk("Error: Could not initialize sensors matrix\n");
		return;
	}

	int iteration = 0;
	while (1)
	{
		uint8_t aMatrix[8][8];

		if (sm.refresh()) {

			sm.getPosition(aMatrix);

#if 0
			printk("Position changed:\n");
			for (int row = 0; row < 8; ++row) {
				for (int col = 0; col < 8; ++col) {
					printk("%3d ", aMatrix[row][col]);  // 3-digit width for alignment
				}
				printk("\n");
			}
			printk("\n");
#endif

			//sm.printCalibrations();

		} else {
			//printk("No changes\n");
		}

		k_msleep(110);
		iteration++;
	}
}

K_THREAD_DEFINE(matrix_id, STACKSIZE, matrix, NULL, NULL, NULL, PRIORITY, 0, 0);


int main(void)
{



#if 0
	while (1)
	{
		sm.test();
		k_msleep(110);
	}
#endif



	printk ("ENDING\n");

	return 0;
//hola
}
