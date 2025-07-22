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
#include <ctype.h>


#include <zephyr/devicetree.h>
#include <zephyr/drivers/adc.h>
#include <zephyr/sys/util.h>


#include "Led.hpp"
#include "SensorsMatrix.h"
#include "UartSender.h"
#include "FlashStorage.h"

#include <zephyr/kernel.h>

#include <zephyr/shell/shell.h>


/* size of stack area used by each thread */
#define STACKSIZE 1024

/* scheduling priority used by each thread */
#define PRIORITY 7

#define LED0_NODE DT_ALIAS(led0)

#if !DT_NODE_HAS_STATUS(LED0_NODE, okay)
#error "Unsupported board: led0 devicetree alias is not defined"
#endif

bool initialized = false;


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


K_SEM_DEFINE(my_sem, 0, 1);  // Initial count = 0, Max count = 1
SensorsMatrix sm;

FlashStorage fs;

void matrix(void)
{
	while (!initialized) k_msleep(1);
        printk("matrix periodic refresh starts.\n");

	int iteration = 0;
	while (1)
	{

		if (sm.refresh()) {
			k_sem_give(&my_sem);
#if 0
			char * buffer = sm.formatVoltages();
			if (buffer) {
				printk("%s", buffer);

				k_free(buffer);
			} else {
				printk("Error. Could not format voltages to be printed");
			}
#endif
	
		} else {
			//printk("No changes\n");
		}


		k_msleep(30);
		iteration++;
	}
}

K_THREAD_DEFINE(matrix_reader_id, 4096, matrix, NULL, NULL, NULL, PRIORITY, 0, 0);

UartSender uart;
void board_monitor(void) {
	uint8_t aMatrix[8][8];
	uint8_t packed_board[8];    // Each byte = 1 row
	char uart_msg[64];          // UART message buffer



	while (!initialized) k_msleep(1);
        printk("board monitor starts.\n");

	while (1) {

		k_sem_take(&my_sem, K_FOREVER);

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
			"BOARD:%02X-%02X-%02X-%02X-%02X-%02X-%02X-%02X\r\n",
			packed_board[7], packed_board[6],
			packed_board[5], packed_board[4],
			packed_board[3], packed_board[2],
			packed_board[1], packed_board[0]);

		// Step 3: Send over UART (use printk or uart_tx)
		printk("Sent: %s", uart_msg);
		uart.send(uart_msg);
	}

	return;
}

K_THREAD_DEFINE(board_monitor_id, STACKSIZE, board_monitor, NULL, NULL, NULL, PRIORITY, 0, 0);

int main(void)
{

	if (fs.initialize() != 0) {
		printk("Error: Could not initialize flash storage\n");
		return -1;
	}

	if (sm.initialize() != 0) {
		printk("Error: Could not initialize sensors matrix\n");
		return -1;
	}

	if (!uart.initialize()) {
		printk("ERROR INITIALIZING Uart");
		return -1;
	}


	storage_data sd;
	if (fs.read(sd) == 0) {
		printk("Calibrations found in flash. Let's use them\n");
		sm.setCalibrations(sd.calibrations);
	} else {
		printk("No calibrations found in flash. Calibrating sensors.\n");
		if (sm.calibrate() != 0) {
			printk("Error: Could not calibrate sensors matrix\n");
			return -1;
		}
	}

	char * buffer = sm.formatCalibrations();
	if (buffer) {
		printk("%s", buffer);
		k_free(buffer);
	}

#if 0
	if (sm.calibrate() != 0) {
		printk("Error: Could not calibrate sensors matrix\n");
	}

	if (sm.calibrate() != 0) {
		printk("Error: Could not calibrate sensors matrix\n");
	}

#endif

	printk("Hw initialized.\n");
	initialized = true;



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




static int cmd_cb_calibrate(const struct shell *shell, size_t argc, char **argv) {
    shell_print(shell, "Calibrating..");

    sm.calibrate();

    return 0;
}

static int cmd_cb_printCalibrations(const struct shell *shell, size_t argc, char **argv) {
	char * buffer = sm.formatCalibrations();
	if (buffer) {
		shell_print(shell, "%s", buffer);

		k_free(buffer);
	} else {
		shell_print(shell, "Error. Could not format calibrations to be printed");
	}



    return 0;
}

static int cmd_cb_saveCalibrations(const struct shell *shell, size_t argc, char **argv) {

	shell_print(shell, "Saving calibrations in flash storage...");
	storage_data sd;
	sm.getCalibrations(sd.calibrations);

	if (fs.write(sd) == 0) {
		shell_print(shell, "SAVED!\n");
	} else {
		shell_print(shell, "ERROR!\n");
	}


    return 0;
}

static int cmd_cb_loadCalibrations(const struct shell *shell, size_t argc, char **argv) {

	shell_print(shell, "Loading calibrations from flash...");
	storage_data sd;
	if (fs.read(sd) == 0) {
		sm.setCalibrations(sd.calibrations);
		shell_print(shell, "LOADED OK!\n");
	} else {
		shell_print(shell, "No calibrations found. Calibrate manually and save them.\n");
	}


    return 0;
}


static int cmd_cb_readmv(const struct shell *shell, size_t argc, char **argv) {
    if (argc != 2) {
        shell_print(shell, "Usage: cb readMv <square>");
        return -EINVAL;
    }

    const char *square = argv[1];

    if (strlen(square) != 2) {
        shell_print(shell, "Invalid format. Square must be 2 characters (e.g., A1).");
        return -EINVAL;
    }

    char file = toupper(square[0]);
    char rank = square[1];

    if (file < 'A' || file > 'H' || rank < '1' || rank > '8') {
        shell_print(shell, "Invalid square. Must be between A1 and H8.");
        return -EINVAL;
    }

    int file_index = file - 'A';  // A=0, B=1, ..., H=7
    int rank_index = 7-(rank - '1');  // 1=0, ..., 8=7

    const int32_t mv = sm.getVoltage(rank_index, file_index);
    shell_print(shell, "%s (%d %d): %dmv", square, file_index, rank_index, mv);

    return 0;
}

static int cmd_cb_readGauss(const struct shell *shell, size_t argc, char **argv) {
    if (argc != 2) {
        shell_print(shell, "Usage: cb readMv <square>");
        return -EINVAL;
    }

    const char *square = argv[1];

    if (strlen(square) != 2) {
        shell_print(shell, "Invalid format. Square must be 2 characters (e.g., A1).");
        return -EINVAL;
    }

    char file = toupper(square[0]);
    char rank = square[1];

    if (file < 'A' || file > 'H' || rank < '1' || rank > '8') {
        shell_print(shell, "Invalid square. Must be between A1 and H8.");
        return -EINVAL;
    }

    int file_index = file - 'A';  // A=0, B=1, ..., H=7
    int rank_index = 7-(rank - '1');  // 1=0, ..., 8=7

    const int32_t gauss = (int32_t)sm.getGauss(rank_index, file_index);
    shell_print(shell, "%s (%d %d): %dG", square, file_index, rank_index, gauss);

    return 0;
}



static int cmd_cb_printVoltages(const struct shell *shell, size_t argc, char **argv) {
	char * buffer = sm.formatVoltages();
	if (buffer) {
		shell_print(shell, "%s", buffer);

		k_free(buffer);
	} else {
		shell_print(shell, "Error. Could not format voltages to be printed");
	}

    return 0;
}



SHELL_STATIC_SUBCMD_SET_CREATE(sub_cb,
    SHELL_CMD(calibrate, NULL, "Sensors calibration", cmd_cb_calibrate),
    SHELL_CMD(printCalibrations, NULL, "print calibrations", cmd_cb_printCalibrations),
    SHELL_CMD(saveCalbrations  , NULL, "save current calibrations to flash", cmd_cb_saveCalibrations),
    SHELL_CMD(loadCalbrations  , NULL, "save current calibrations to flash", cmd_cb_loadCalibrations),

    SHELL_CMD(readMv,    NULL, "mv of a square", cmd_cb_readmv),
    SHELL_CMD(readGauss, NULL, "gauss of a square", cmd_cb_readGauss),
    SHELL_CMD(printVoltages, NULL, "Print voltages matrix", cmd_cb_printVoltages),
    SHELL_SUBCMD_SET_END /* Obligatorio para cerrar la lista */
);

SHELL_CMD_REGISTER(cb, &sub_cb, "Chessboard debug commands", NULL);



