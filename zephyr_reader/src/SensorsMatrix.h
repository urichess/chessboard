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

    explicit SensorsMatrix() {}

    int initialize();

    void getPosition(uint8_t aMatrix[8][8]);

    bool refresh();

    void printCalibrations();

    void test();

    protected:

    void select(uint8_t sensor);

    void readGauss(uint8_t aMatrix[8][8]);

    private:

};

#endif /* __SENSORS_MATRIX_H__ */
