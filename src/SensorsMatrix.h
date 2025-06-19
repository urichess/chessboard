#ifndef __SENSORS_MATRIX_H__
#define __SENSORS_MATRIX_H__

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/__assert.h>
#include <string.h>


#include <zephyr/devicetree.h>
#include <zephyr/drivers/adc.h>
#include <zephyr/sys/util.h>

class SensorsMatrix
{
    public:

    explicit SensorsMatrix(const struct gpio_dt_spec * gpios_mux, const struct adc_dt_spec * adc_channels) : gpios_mux_(gpios_mux), adc_channels_(adc_channels) {}

    int initialize();

    void read(uint8_t aMatrix[8][8]);

    protected:

    void select(uint8_t sensor);

    private:

    const struct gpio_dt_spec * gpios_mux_;
    const struct adc_dt_spec * adc_channels_;
};

#endif /* __SENSORS_MATRIX_H__ */
