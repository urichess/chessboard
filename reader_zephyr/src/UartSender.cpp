#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/uart.h>
#include <stdio.h>
#include <string.h>

#include "UartSender.h"

#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(uartsender, LOG_LEVEL_DBG);  // or LOG_LEVEL_DBG

const struct device *uart_dev = DEVICE_DT_GET(DT_CHOSEN(uart_sender));

static char last_msg_[128] = {0};
static char rx_line_buf[128];
static size_t rx_line_pos = 0;


//This is a placeholder for a protocol. there should be another thread processing messages and that thread should be doing this.
static void uart_cb(const struct device *dev, void *user_data) {
	
    UartSender* theSender = static_cast<UartSender*>(user_data);

    while (uart_irq_update(dev) && uart_irq_is_pending(dev)) {
        if (uart_irq_rx_ready(dev)) {
            uint8_t buf[64];
            int recv_len = uart_fifo_read(dev, buf, sizeof(buf));
            for (int i = 0; i < recv_len; i++) {
                char c = buf[i];
                if (c == '\n' || rx_line_pos >= sizeof(rx_line_buf) - 1) {
                    rx_line_buf[rx_line_pos] = '\0';
                    if (strcmp(rx_line_buf, "REQUEST:1") == 0) {
                        if (theSender) {
                            theSender->resend();
                        }
                    }
                    rx_line_pos = 0; // Reset for next line
                } else if (c != '\r') {
                    rx_line_buf[rx_line_pos++] = c;
                }
            }
        }
    }
	
}

bool UartSender::initialize() {
	if (!device_is_ready(uart_dev)) {
		LOG_ERR("%s uart device for uartsender is not ready\n", __func__);
		return false;
	}

	uart_irq_callback_user_data_set(uart_dev, uart_cb, this);
    uart_irq_rx_enable(uart_dev);

	LOG_INF("uart sender initialized..OK\n");
	return true;
}

void UartSender::send(const char *msg) {
	strncpy(last_msg_, msg, sizeof(last_msg_) - 1);
    for (size_t i = 0; i < strlen(msg); i++) {
        uart_poll_out(uart_dev, msg[i]);
    }
}

void UartSender::resend() {
	send(last_msg_);
}