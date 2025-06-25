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

		if (sm.refresh()) {

			uint8_t aMatrix[8][8];
			uint8_t packed_board[8];    // Each byte = 1 row
			char uart_msg[64];          // UART message buffer
			sm.getPosition(aMatrix);



			// Step 1: Pack each row into a byte
			    for (int row = 0; row < 8; ++row) {
				uint8_t bits = 0;

				for (int col = 0; col < 8; ++col) {
				    if (aMatrix[row][col]) {
					bits |= (1 << (7 - col));  // col 0 is MSB
				    }
				}

				packed_board[row] = bits;
			    }

			    // Step 2: Format UART message as one hex string
			    int len = snprintf(uart_msg, sizeof(uart_msg),
					       "BOARD:%02X-%02X-%02X-%02X-%02X-%02X-%02X-%02X",
					       packed_board[0], packed_board[1],
					       packed_board[2], packed_board[3],
					       packed_board[4], packed_board[5],
					       packed_board[6], packed_board[7]);

			    // Step 3: Send over UART (use printk or uart_tx)
			    printk("%s\n", uart_msg);



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



//	printk ("ENDING\n");

	return 0;
//hola
}
