#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/uart.h>
#include <stdio.h>
#include <string.h>

#include "UartSender.h"

#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(uartsender, LOG_LEVEL_DBG);  // or LOG_LEVEL_DBG

const struct device *uart_dev = DEVICE_DT_GET(DT_CHOSEN(uart_sender));

bool UartSender::initialize() {
	if (!device_is_ready(uart_dev)) {
		LOG_ERR("%s uart device for uartsender is not ready\n", __func__);
		return false;
	}

	LOG_INF("uart sender initialized..OK\n");
	return true;
}

void UartSender::send(const char *msg) {
    for (size_t i = 0; i < strlen(msg); i++) {
        uart_poll_out(uart_dev, msg[i]);
    }
}
