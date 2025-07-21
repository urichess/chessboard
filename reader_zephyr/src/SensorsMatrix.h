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

    int calibrate();

    void getCalibrations(int32_t aMatrix[8][8]);

    void setCalibrations(int32_t aMatrix[8][8]);

    bool refresh();

    void getPosition(uint8_t aMatrix[8][8]);

    char * formatCalibrations();

    char * formatVoltages();

    int32_t getVoltage(uint8_t i, uint8_t j);

    float getGauss(uint8_t i, uint8_t j);

    protected:

    void select(uint8_t sensor);

    void readVoltages(); // called in a thread appart

    private:

};

#endif /* __SENSORS_MATRIX_H__ */
