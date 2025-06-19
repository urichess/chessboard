#ifndef __UTILS_H__
#define __UTILS_H__

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/__assert.h>
#include <string.h>


#include <zephyr/devicetree.h>
#include <zephyr/drivers/adc.h>
#include <zephyr/sys/util.h>

int32_t readMv(const struct adc_dt_spec * adc_spec);

float readGauss(const struct adc_dt_spec * adc_spec, int32_t aCalibration);

float millivoltsToGauss(int32_t millivolts, int32_t referenceMillivolts);

#endif /*__UTILS_H__*/
