#include "SensorsMatrix.h"
#include "utils.h"

#include <zephyr/logging/log.h>

#include "LockObjects.h"

LOG_MODULE_REGISTER(sensormatrix, LOG_LEVEL_DBG);  // or LOG_LEVEL_DBG

#ifndef CONFIG_DETECTION_HISTERESYS_EMPTY
#define CONFIG_DETECTION_HISTERESYS_EMPTY 15
#endif

#ifndef CONFIG_DETECTION_HISTERESYS_PIECE
#define CONFIG_DETECTION_HISTERESYS_PIECE 50
#endif

static const int32_t histeresys_empty_mv = gauss2mv(CONFIG_DETECTION_HISTERESYS_EMPTY);
static const int32_t histeresys_piece_mv = gauss2mv(CONFIG_DETECTION_HISTERESYS_PIECE);

#define NROWS 8
#define NFILES 8

#define BUFFER_SIZE 3 // buffer used to filter position changes.

#if !DT_NODE_EXISTS(DT_PATH(zephyr_user)) || \
	!DT_NODE_HAS_PROP(DT_PATH(zephyr_user), io_channels) || \
	!DT_NODE_HAS_PROP(DT_PATH(zephyr_user), mux_gpios) || \
	!DT_NODE_HAS_PROP(DT_PATH(zephyr_user), enable_gpios)
#error "Unsupported board: zephyr_user devicetree alias is not defined"
#endif

#define DT_SPEC_AND_COMMA(node_id, prop, idx) \
	ADC_DT_SPEC_GET_BY_IDX(node_id, idx),

/* Data of ADC io-channels specified in devicetree. */
static const struct adc_dt_spec adc_channels[] = {
	DT_FOREACH_PROP_ELEM(DT_PATH(zephyr_user), io_channels,
			     DT_SPEC_AND_COMMA)
};

#define DT_GPIO_SPEC_AND_COMMA(node_id, prop, idx) \
	GPIO_DT_SPEC_GET_BY_IDX(node_id, prop, idx),


static const struct gpio_dt_spec gpios_mux[] = {
	DT_FOREACH_PROP_ELEM(DT_PATH(zephyr_user), mux_gpios,
			     DT_GPIO_SPEC_AND_COMMA)
};

static const struct gpio_dt_spec enable_gpios[] = {
	DT_FOREACH_PROP_ELEM(DT_PATH(zephyr_user), enable_gpios,
			     DT_GPIO_SPEC_AND_COMMA)
};

int32_t calibrations[NROWS][NFILES] = {0}; // mv. used to find the 0

int32_t voltages[BUFFER_SIZE][NROWS][NFILES] = {0};
uint8_t current = 0;
uint8_t previous = 0;

uint8_t currentPosition[NROWS][NFILES] = {0}; // 0-empty and 1-piece

K_MUTEX_DEFINE(my_mutex);
K_MUTEX_DEFINE(calib_mutex);

int SensorsMatrix::initialize()
{
	LOG_DBG ("SensorsMatrix::initialize() Initializing Sensors Matrix...");
	int ret;
	int err;
	uint16_t buf;
	struct adc_sequence sequence = {
		.buffer = &buf,
		.buffer_size = sizeof(buf), /* buffer size in bytes, not number of samples */
	};

	if (ARRAY_SIZE(adc_channels) != 4)
	{
		LOG_ERR("Error: Expected 4 elements in adc_channels");
		return -1;
	}

	if (ARRAY_SIZE(gpios_mux) != 4)
	{
		LOG_ERR("Error: Expected 4 elements in gpios_mux");
		return -1;
	}

	if (ARRAY_SIZE(enable_gpios) != 1)
	{
		LOG_ERR("Error: Expected 1 elements in enable_gpios");
		return -1;
	}


	/* Configure channels individually prior to sampling. */
	for (size_t i = 0U; i < 4; i++) {
		if (!adc_is_ready_dt(&adc_channels[i])) {
			LOG_ERR("SensorsMatrix::initialize() ADC controller device %s not ready", adc_channels[i].dev->name);
			return -1;
		}

		err = adc_channel_setup_dt(&adc_channels[i]);
		if (err < 0) {
			LOG_ERR("SensorsMatrix::initialize() Could not setup channel #%d (%d)", i, err);
			return -1;
		}

		LOG_DBG("Configuted ADC CHANNEL %d", adc_channels[i].channel_id);
	}

	/* Configure mux gpios */
	for (size_t nmux = 0U; nmux < 4; nmux++)
	{
		const struct gpio_dt_spec *spec = &gpios_mux[nmux];
		if (!device_is_ready(spec->port)) {
			LOG_ERR("SensorsMatrix::initialize() Error: %s device is not ready", spec->port->name);
			return -1;
		}

		ret = gpio_pin_configure_dt(spec, GPIO_OUTPUT);
		if (ret != 0) {
			LOG_ERR("SensorsMatrix::initialize() Error: failed to configure %s", spec->port->name);
			return -1;
		}

		LOG_DBG("Configuted port %s pin %d as GPIO_OUTPUT", spec->port->name, spec->pin);

		gpio_pin_set(spec->port, spec->pin, 0);
	}


	if (!device_is_ready(enable_gpios->port)) {
		LOG_ERR("SensorsMatrix::initialize() Error: %s device is not ready", enable_gpios->port->name);
		return -1;
	}

	ret = gpio_pin_configure_dt(enable_gpios, GPIO_OUTPUT);
	if (ret != 0) {
		LOG_ERR("SensorsMatrix::initialize() Error: failed to configure %s", enable_gpios->port->name);
		return -1;
	}

	gpio_pin_set(enable_gpios->port, enable_gpios->pin, 0); // 0 to enable
								//
	LOG_INF ("SensorsMatrix::initialize() Initialized Sensors Matrix...OK Histeresis(%dG-%dG (%dmV-%dmV))", (int32_t)CONFIG_DETECTION_HISTERESYS_EMPTY, (int32_t)CONFIG_DETECTION_HISTERESYS_PIECE, histeresys_empty_mv, histeresys_piece_mv);

	return 0;
}

int SensorsMatrix::calibrate() {
	ScopedLock sl(&calib_mutex);

	LOG_INF ("Waitting 5s");
	k_msleep(5000);

	LOG_INF("SensorsMatrix::calibrate() Calculating calibrations...");
	for (int i = 0; i < 16; i++) {
		select(i);

		const int row0 = i/NROWS;
		const int iRow[4] = {row0, row0+2, row0+4, row0+6 };
		const int file = i%NFILES;

		for (int r=0; r<4; r++) {
			const int theRow = iRow[r];

			// Filtering calibrations

			int32_t mv[5];
			for (int s = 0; s<5; s++) {
				mv[s] = readMv(&adc_channels[r]);
				//k_msleep(1);
			}
			calibrations[file][theRow] = torben_median_filter(mv, 5);
		}
	}

	LOG_INF ("SensorsMatrix::calibrate() Calculated calibrations...OK");
	return 0;
}

void SensorsMatrix::setCalibrations(int32_t cals[8][8]) {
	ScopedLock sl(&calib_mutex);

	memcpy(calibrations, cals, sizeof(calibrations));
}

void SensorsMatrix::getCalibrations(int32_t cals[8][8]) {
	ScopedLock sl(&calib_mutex);
	
	memcpy(cals, calibrations, sizeof(calibrations));
}

void SensorsMatrix::getPosition(uint8_t aMatrix[8][8])
{
	ScopedLock sl(&my_mutex);

	memcpy (aMatrix, currentPosition, 64);
}

void SensorsMatrix::readVoltages() {
	previous = current;
	current++;
	if (current >= BUFFER_SIZE) {
		current = 0;
	}

	for (int i = 0; i < 16; i++) {
	    select(i);

	    const int row0 = i/NROWS;
	    const int iRow[4] = {row0, row0+2, row0+4, row0+6 };
	    const int file = i%NFILES;

	    for (int r=0; r<4; r++)
	    {
	      const int theRow = iRow[r];
	      voltages[current][file][theRow] = readMv(&adc_channels[r]);
	    }
	}
}

bool SensorsMatrix::refresh()
{
	bool changed = false;

	readVoltages();

	ScopedLock sl(&my_mutex);

	for (int i = 0; i<8; i++) {
		for (int j=0; j<8; j++) {
			bool allGreaterThanHighLimit = true;
			bool allLowerThanLowLimit = true;
			int32_t signOfAll = 0;

			for (int k = 0; k < BUFFER_SIZE; k++) {
				const int32_t signedCalibratedVoltage = voltages[k][i][j] - calibrations[i][j];
				const int32_t calibratedVoltage = signedCalibratedVoltage<0? -signedCalibratedVoltage: signedCalibratedVoltage;
				signOfAll = signedCalibratedVoltage;
				if (calibratedVoltage < histeresys_piece_mv ) allGreaterThanHighLimit = false;
				if (calibratedVoltage > histeresys_empty_mv ) allLowerThanLowLimit = false;
			}

			if ( currentPosition[i][j] == 1 && allLowerThanLowLimit) {
				changed = true;
				currentPosition[i][j] = 0;
			} else if ( currentPosition[i][j] == 0 && allGreaterThanHighLimit) {
				changed = true;
				currentPosition[i][j] = (signOfAll > 0)? 1 : 2;
			}
		}	
	}

	return changed;
}

int32_t SensorsMatrix::getVoltage(uint8_t i, uint8_t j) {
	return voltages[current][i][j];
}

float SensorsMatrix::getGauss(uint8_t i, uint8_t j) {
	return mv2Gauss(voltages[current][i][j] - calibrations[i][j]);
}

void SensorsMatrix::select(uint8_t number) {
	if (number > 15) {
		number = 15;
	}
  
	gpio_pin_set(gpios_mux[0].port, gpios_mux[0].pin, (number & 0b0001)); // Set bit 0
	gpio_pin_set(gpios_mux[1].port, gpios_mux[1].pin, (number & 0b0010)); // Set bit 1
	gpio_pin_set(gpios_mux[2].port, gpios_mux[2].pin, (number & 0b0100)); // Set bit 2
	gpio_pin_set(gpios_mux[3].port, gpios_mux[3].pin, (number & 0b1000)); // Set bit 3

	k_usleep(10);
}

char * SensorsMatrix::formatCalibrations() {
	return formatVoltagesMatrix(calibrations);
}

char * SensorsMatrix::formatVoltages() {
	return formatVoltagesMatrix(voltages[current]);
}
