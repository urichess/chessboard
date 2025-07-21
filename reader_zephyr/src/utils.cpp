#include "utils.h"

#ifndef CONFIG_SAMPLES_FOR_TORBEN
#define CONFIG_SAMPLES_FOR_TORBEN 5
#endif

int32_t torben_median_filter(int32_t *arr, int size)
{
    int32_t min = arr[0], max = arr[0], guess, maxltguess, mingtguess;
    int i, less, greater, equal;

    // Encuentra el valor mínimo y máximo en el array
    for (i = 1; i < size; i++) {
        if (arr[i] < min) min = arr[i];
        if (arr[i] > max) max = arr[i];
    }

    // Bucle principal que busca la mediana
    while (min < max) {
        guess = (min + max) / 2;
        less = greater = equal = 0;
        maxltguess = min;
        mingtguess = max;

        for (i = 0; i < size; i++) {
            if (arr[i] < guess) {
                less++;
                if (arr[i] > maxltguess) maxltguess = arr[i];
            } else if (arr[i] > guess) {
                greater++;
                if (arr[i] < mingtguess) mingtguess = arr[i];
            } else {
                equal++;
            }
        }

        // Si la cantidad de elementos menores o mayores es suficiente para encontrar la mediana
        if (less <= size / 2 && greater <= size / 2) {
            if (less >= size / 2) return maxltguess;
            if (greater >= size / 2) return mingtguess;
            return guess;
        } else if (less > greater) {
            max = maxltguess;  // Ajusta el límite superior a maxltguess
        } else {
            min = mingtguess;  // Ajusta el límite inferior a mingtguess
        }

        // Si min y max se acercan lo suficiente, devolver min o max
        if (min == max) break;
    }

    // Si el bucle termina, devolvemos min (o max, ya que min == max)
    return min;
}

int32_t internalRead(const struct adc_dt_spec * adc_spec)
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

int32_t readMv(const struct adc_dt_spec * adc_spec)
{
	int32_t mv[CONFIG_SAMPLES_FOR_TORBEN];

	for (int s = 0; s<CONFIG_SAMPLES_FOR_TORBEN; s++) {
		mv[s] = internalRead(adc_spec);
	}
	return torben_median_filter(mv, CONFIG_SAMPLES_FOR_TORBEN);
}

/*
float readGauss(const struct adc_dt_spec * adc_spec, int32_t aCalibration)
{
    const int32_t mv = readMv(adc_spec);
    const float gauss = millivoltsToGauss(mv, aCalibration);
    return gauss;
}
*/

float millivoltsToGauss(int32_t millivolts, int32_t referenceMillivolts)
{
  float gauss = mv2Gauss(millivolts - referenceMillivolts);
  return gauss<0?-gauss:gauss; // ??
}

char* formatVoltagesMatrix(uint32_t aMatrix[8][8]) {
	//const size_t buf_size = (NFILES * 4 + 2) * NROWS + 32; // Estimate
	const size_t buf_size = 512;
	char* buf = (char*)k_malloc(buf_size);
	if (!buf) {
		printk("ERROR: SensorsMatrix::formatMatrix() Allocation failed (%d)\n", buf_size);
		return nullptr; // Allocation failed
	}

	char* p = buf;
	char* end = buf + buf_size;

	for (int row = 0; row < 8; ++row) {
		for (int col = 0; col < 8; ++col) {
			if (p + 4 >= end) {
				k_free(buf);
				printk("ERROR: SensorsMatrix::formatMatrix() Small buffer A (%d)\n", buf_size);
				return nullptr;
			}
			p += sprintf(p, "%3d ", aMatrix[row][col]);
		}
		if (p + 2 >= end) {
			k_free(buf);
			printk("ERROR: SensorsMatrix::formatMatrix() Small buffer B (%d)\n", buf_size);
			return nullptr;
		}
		*p++ = '\r';
		*p++ = '\n';
	}
	*p = '\0';

	return buf; // Caller must free it with k_free()
}
