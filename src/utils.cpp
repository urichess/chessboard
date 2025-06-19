#include "utils.h"

#ifndef CONFIG_SAMPLES_FOR_TORBEN
#define CONFIG_SAMPLES_FOR_TORBEN 5
#endif

#ifndef CONFIG_MV_PER_GAUSS
#define CONFIG_MV_PER_GAUSS 2
#endif


int32_t readMv(const struct adc_dt_spec * adc_spec)
{
	int32_t val_mv = -1;
	int err;
	uint16_t buf;

	struct adc_sequence sequence = {
		.buffer = &buf,
		/* buffer size in bytes, not number of samples */
		.buffer_size = sizeof(buf),
	};


	(void)adc_sequence_init_dt(adc_spec, &sequence);

	err = adc_read_dt(adc_spec, &sequence);
	if (err < 0) {
		printk("Could not read (%d)\n", err);
		return -1;
	}

	/*
	 * If using differential mode, the 16 bit value pin
	 * in the ADC sample buffer should be a signed 2's
	 * complement value.
	 */
	if (adc_spec->channel_cfg.differential) {
		val_mv = (int32_t)((int16_t)buf);
	} else {
		val_mv = (int32_t)buf;
	}
	//printk("%"PRId32, val_mv);
	err = adc_raw_to_millivolts_dt(adc_spec,
					   &val_mv);
	/* conversion to mV may not be supported, skip if not */
	if (err < 0) {
		printk(" (value in mV not available)\n");
		return -1;
	}

	return val_mv;
}

float readGauss(const struct adc_dt_spec * adc_spec, int32_t aCalibration)
{
    const int32_t mv = readMv(adc_spec);
    const float gauss = millivoltsToGauss(mv, aCalibration);
    return gauss;
}

float millivoltsToGauss(int32_t millivolts, int32_t referenceMillivolts)
{
  float gauss = 1.0 * (millivolts - referenceMillivolts) / CONFIG_MV_PER_GAUSS;
  return gauss<0?-gauss:gauss; // ??
}
