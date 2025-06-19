#include "SensorsMatrix.h"
#include "utils.h"

#ifndef CONFIG_DETECTION_HISTERESYS_EMPTY
#define CONFIG_DETECTION_HISTERESYS_EMPTY 10
#endif

#ifndef CONFIG_DETECTION_HISTERESYS_PIECE
#define CONFIG_DETECTION_HISTERESYS_PIECE 30
#endif

#define NROWS 8
#define NFILES 8

int32_t calibrations[NROWS][NFILES] = {0};

uint8_t calculateState(uint8_t currentState, float gauss)
{
    // Adding histeresys
    if (currentState == 1)
    {
      return gauss<CONFIG_DETECTION_HISTERESYS_EMPTY? 0:1;
    }
    
    return gauss>CONFIG_DETECTION_HISTERESYS_PIECE? 1:0;
}




int SensorsMatrix::initialize()
{
	printk ("SensorsMatrix::initialize() Initializing Sensors Matrix...");
	int ret;
	int err;
	uint32_t count = 0;
	uint16_t buf;
	struct adc_sequence sequence = {
		.buffer = &buf,
		.buffer_size = sizeof(buf), /* buffer size in bytes, not number of samples */
	};

	/* Configure channels individually prior to sampling. */
	for (size_t i = 0U; i < ARRAY_SIZE(adc_channels_); i++) {
		if (!adc_is_ready_dt(&adc_channels_[i])) {
			printk("SensorsMatrix::initialize() ADC controller device %s not ready\n", adc_channels_[i].dev->name);
			return -1;
		}

		err = adc_channel_setup_dt(&adc_channels_[i]);
		if (err < 0) {
			printk("SensorsMatrix::initialize() Could not setup channel #%d (%d)\n", i, err);
			return -1;
		}
	}

	/* Configure mux gpios */
	for (size_t nmux = 0U; nmux < ARRAY_SIZE(gpios_mux_); nmux++)
	{
		const struct gpio_dt_spec *spec = &gpios_mux_[nmux];
		if (!device_is_ready(spec->port)) {
			printk("SensorsMatrix::initialize() Error: %s device is not ready\n", spec->port->name);
			return -1;
		}

		ret = gpio_pin_configure_dt(spec, GPIO_OUTPUT);
		if (ret != 0) {
			printk("SensorsMatrix::initialize() Error: failed to configure %s\n", spec->port->name);
			return -1;
		}

		gpio_pin_set(spec->port, spec->pin, 0);
	}

# if 0

  // Configure GPIO pins as outputs
  pinMode(gpioEnable_, OUTPUT);
  digitalWrite(gpioEnableMuxs, LOW);

#endif

	k_msleep(1000);

	printk ("SensorsMatrix::initialize() Initialized Sensors Matrix...OK\n");

	printk ("SensorsMatrix::initialize() Calculating calibrations...\n");
	for (int i = 0; i < 16; i++) {
		select(i);

		const int row0 = i/NROWS;
		const int iRow[4] = {row0, row0+2, row0+4, row0+6 };
		const int file = i%NFILES;

		for (int r=0; r<4; r++) {
			const int theRow = iRow[r];

			// Filtering calibrations
#if 0
			float mv[5];
			for (int s = 0; s<5; s++) {
				mv[s] = readMv(adcSensors_[r]);
				delay(1);
			}
			calibrations[theRow][file] = torben_median_filter(mv, 5);
#endif
			calibrations[theRow][file] = readMv(&adc_channels_[r]); // No torben mogensen?
		}
	}

	printk ("SensorsMatrix::initialize() Calculated calibrations...OK\n");

# if 0
  Serial.println ("Calibrations: ");
    for (int i=0; i<8; i++)
    {
        for (int j=0; j<8; j++)
        {
        Serial.print (calibrations[i][j]);
        Serial.print (" ");
        }
        Serial.println (" ");
    }
    Serial.println ("--------------------");
#endif
    return 0;
}

void SensorsMatrix::read(uint8_t aMatrix[8][8])
{
  for (int i = 0; i < 16; i++) {
    select(i);

    const int row0 = i/NROWS;
    const int iRow[4] = {row0, row0+2, row0+4, row0+6 };
    const int file = i%NFILES;

    for (int r=0; r<4; r++)
    {
      const int theRow = iRow[r];

      const float gauss = readGauss(&adc_channels_[r], calibrations[theRow][file]);
      aMatrix[theRow][file] = (uint8_t)gauss; //calculateState (aMatrix[theRow][file], gauss);
    }
  }
}

void SensorsMatrix::select(uint8_t number) {
  if (number > 15) {
    number = 15;
  }
  
  gpio_pin_set(gpios_mux_[0].port, gpios_mux_[0].pin, (number & 0b0001)); // Set bit 0
  gpio_pin_set(gpios_mux_[1].port, gpios_mux_[1].pin, (number & 0b0010)); // Set bit 0
  gpio_pin_set(gpios_mux_[2].port, gpios_mux_[2].pin, (number & 0b0100)); // Set bit 0
  gpio_pin_set(gpios_mux_[3].port, gpios_mux_[3].pin, (number & 0b1000)); // Set bit 0

  k_usleep(1);
}
