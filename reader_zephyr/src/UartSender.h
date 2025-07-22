#ifndef __UART_SENDER_H__
#define __UART_SENDER_H__

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/__assert.h>
#include <string.h>


#include <zephyr/devicetree.h>
#include <zephyr/drivers/adc.h>
#include <zephyr/sys/util.h>

class UartSender
{
public:

    explicit UartSender() {}

    bool initialize();

    void send(const char*);

protected:

private:

};

#endif /* __SENSORS_MATRIX_H__ */
