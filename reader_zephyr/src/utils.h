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

#ifndef CONFIG_MV_PER_GAUSS
#define CONFIG_MV_PER_GAUSS 2
#endif

#define gauss2mv(x) (int32_t)((float)(x)*CONFIG_MV_PER_GAUSS)
#define mv2Gauss(x) (float)((float)(x)/CONFIG_MV_PER_GAUSS)

int32_t torben_median_filter(int32_t *arr, int size);

int32_t readMv(const struct adc_dt_spec * adc_spec);

float millivoltsToGauss(int32_t millivolts, int32_t referenceMillivolts);

char* formatVoltagesMatrix(int32_t aMatrix[8][8]);

#endif /*__UTILS_H__*/
