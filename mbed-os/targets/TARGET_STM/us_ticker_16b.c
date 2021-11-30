/* mbed Microcontroller Library
 * Copyright (c) 2006-2016 ARM Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#include <stddef.h>
#include "us_ticker_api.h"
#include "PeripheralNames.h"
#include "hal_tick.h"

// A 16-bit timer is used
#if TIM_MST_16BIT

TIM_HandleTypeDef TimMasterHandle;

volatile uint32_t ghi_timeCounterH = 0;

volatile uint32_t ghi_counter;
volatile uint32_t ghi_counter2;
volatile uint32_t ghi_timestamp;

static int us_ticker_inited = 0;

void set_compare(uint16_t count)
{
    TimMasterHandle.Instance = TIM_MST;
    // Set new output compare value
    __HAL_TIM_SET_COMPARE(&TimMasterHandle, TIM_CHANNEL_1, count);
    // Enable IT
    __HAL_TIM_ENABLE_IT(&TimMasterHandle, TIM_IT_CC1);
}

void us_ticker_init(void)
{
    if (us_ticker_inited) return;
    us_ticker_inited = 1;

    TimMasterHandle.Instance = TIM_MST;
	
	ghi_counter = 0;
	ghi_counter2 = 0;
	ghi_timestamp = 0;

    HAL_InitTick(0); // The passed value is not used
	
	
}

uint32_t us_ticker_read()
{
  
    TimMasterHandle.Instance = TIM_MST;

    if (!us_ticker_inited) 
		us_ticker_init();
    
    ghi_counter = (uint32_t)(ghi_timeCounterH << 16) | TIM_MST->CNT;
	
	if (ghi_counter < ghi_counter2) {
		ghi_timeCounterH++;	
		
		ghi_counter = (uint32_t)(ghi_timeCounterH << 16) | TIM_MST->CNT;
	}
		
	ghi_counter2 = ghi_counter;
		
    return ghi_counter;

}

void us_ticker_set_interrupt(timestamp_t timestamp)
{    
	uint32_t t = (uint32_t)timestamp;
	
	if (t <=  us_ticker_read()) { // This event was in the past
        us_ticker_irq_handler();
    } else {
		ghi_timestamp =  t;
        set_compare(ghi_timestamp & 0xFFFF);
    }	
}

void us_ticker_disable_interrupt(void)
{
    TimMasterHandle.Instance = TIM_MST;
    __HAL_TIM_DISABLE_IT(&TimMasterHandle, TIM_IT_CC1);
}

void us_ticker_clear_interrupt(void)
{
    TimMasterHandle.Instance = TIM_MST;
    if (__HAL_TIM_GET_FLAG(&TimMasterHandle, TIM_FLAG_CC1) == SET) {
        __HAL_TIM_CLEAR_FLAG(&TimMasterHandle, TIM_FLAG_CC1);
    }
}

#endif // TIM_MST_16BIT
