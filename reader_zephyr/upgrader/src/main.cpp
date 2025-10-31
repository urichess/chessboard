/*
 * Copyright (c) 2017 Linaro Limited
 *
 * SPDX-License-Identifier: Apache-2.0
 */


#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/adc.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/util.h>
#include <zephyr/sys/__assert.h>
#include <zephyr/shell/shell.h>

//#include <zephyr/bootutil/bootutil_public.h>

#include <zephyr/dfu/mcuboot.h>
#include <zephyr/sys/reboot.h>

#include <string.h>
#include <ctype.h>

#include "Led.hpp"

/* size of stack area used by each thread */
#define STACKSIZE 1024

/* scheduling priority used by each thread */
#define PRIORITY_NORMAL 7
#define PRIORITY_HIGH 5

#define LED0_NODE DT_ALIAS(led0)

#if !DT_NODE_HAS_STATUS(LED0_NODE, okay)
#error "Unsupported board: led0 devicetree alias is not defined"
#endif

extern "C" int main(void)
{
    printk("Updater running (slot 1). Simulating update for 10 seconds...\n");
    k_sleep(K_SECONDS(10));

    printk("Update simulation done. Marking Slot 1 as confirmed so MCUboot returns to Slot 0.\n");

    // Tell MCUboot we are finished with Slot 1
    //boot_write_img_confirmed();
    //boot_write_img_confirmed_multi(0);
    //    boot_set_confirmed();

    printk("Rebooting to boot Slot 0...\n");
    //sys_reboot(SYS_REBOOT_COLD);


    return 0;
}

