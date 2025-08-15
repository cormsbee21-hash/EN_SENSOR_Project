import utime
import uasyncio as asyncio
from machine import Pin
from time import ticks_ms, ticks_diff

# Pin configurations
# StopLight
redled = Pin(5, Pin.OUT)
yellowled = Pin(4, Pin.OUT)
greenled = Pin(3, Pin.OUT)

# Crash Sensor
Led = Pin(13, Pin.OUT)
Shock = Pin(15, Pin.IN, Pin.PULL_UP) # Use internal pull-up resistor
#Ultrasonic Sensor
inputPin = Pin(26, Pin.IN)  # ECHO pin to GP26 blue wire
outputPin = Pin(27, Pin.OUT) # TRIG pin to GP27 purple wire

# Global variables
arm_status = 0 # unarmed
crash_val = 0 # Initialize crash sensor value
target_engagement = 0

# Crash Sensor Reading
async def read_crash():
    global crash_val
    
    crash_val = Shock.value()
    Led.value(not crash_val) # Assuming active low for LED

# Set the traffic light based on arm_status
async def set_light():
    global arm_status, crash_val
    if arm_status == 0:
        redled.value(0)
        yellowled.value(0)
        greenled.value(1)
    elif arm_status == 1 and crash_val:
        redled.value(0)
        yellowled.value(1)
        greenled.value(0)
    elif arm_status == 1 and not crash_val:
        redled.value(1)
        yellowled.value(0)
        greenled.value(0)
    elif arm_status == 1 and crash_val:
        redled.value(1)
        yellowled.value(1)
        greenled.value(1)
    else:
        redled.value(1)
        yellowled.value(0)
        utime.sleep_ms(50)
        redled.value(0)
        greenled.value(1)
        utime.sleep_ms(50)
        greenled.value(0)
        yellowled.value(1)
        utime.sleep_ms(50)        
    
# Ultrasonic sensor reading
async def read_ultrasonic_ranger():
    global arm_status
    outputPin.value(0)
    utime.sleep_us(2)
    outputPin.value(1)
    utime.sleep_us(10)
    outputPin.value(0)

    # Read the pulse duration on the ECHO pin
    start_time = utime.ticks_us()
    timeout = 25000
    while inputPin.value() == 0 and utime.ticks_diff(utime.ticks_us(), start_time) < timeout:
        await asyncio.sleep_ms(1) # Yield to other tasks

    start_pulse = utime.ticks_us()
    while inputPin.value() == 1 and utime.ticks_diff(utime.ticks_us(), start_pulse) < timeout:
        await asyncio.sleep_ms(1) # Yield to other tasks

    end_pulse = utime.ticks_us()
    duration = utime.ticks_diff(end_pulse, start_pulse)
    
    # Transform pulse duration to distance
    distance = duration / 58

    if distance < 20:
        arm_status = 1
    else:
        arm_status = 0
        
    print("Distance:", distance, "cm")
    
async def read_serial():
    global target_engagement
    while True:
        # The select call is correct, but let's make sure the display is updated
        # with the received data.
        if select.select([sys.stdin], [], [], 0)[0]:
            try:
                line = sys.stdin.readline().strip()
                if line: # Only update if we received a non-empty string
                    await target_engagement = 1
            except Exception as e:
                sys.print_exception(e)
        
        await asyncio.sleep_ms(50)
        
# Main asynchronous loop
async def main():
    while True:
        asyncio.create_task(read_serial())
        await asyncio.gather(
            read_crash(),
            set_light(),
            read_ultrasonic_ranger()
        )
        
        await asyncio.sleep(.2) # Pause asynchronously for 2 seconds

if __name__ == "__main__":
    asyncio.run(main())