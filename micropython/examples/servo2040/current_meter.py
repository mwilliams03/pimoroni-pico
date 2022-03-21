import time
from machine import Pin
from pimoroni import Analog, AnalogMux, Button
from plasma import WS2812
from servo import ServoCluster, servo2040

# NOTE: ServoCluster lets you control up to 30 servos at once. This is
# done using the RP2040's PIO system. As such it is experimental and may
# have edge-cases that will need to be fixed. This is particularly true
# when attempting to run a program multiple times.
# If you do encounter issues, try resetting your board.

# Press "Boot" to exit the program.

BRIGHTNESS = 0.4      # The brightness of the LEDs
UPDATES = 50          # How many times to update LEDs and Servos per second
MAX_CURRENT = 3.0     # The maximum current, in amps, to show on the meter
SAMPLES = 50          # The number of current measurements to take per reading
TIME_BETWEEN = 0.001  # The time between each current measurement

# Create the user button
user_sw = Button(servo2040.USER_SW)

# Create a servo cluster for pins 0 to 7, using PIO 0 and State Machine 0
START_PIN = servo2040.SERVO_1
END_PIN = servo2040.SERVO_8
servos = ServoCluster(pio=0, sm=0, pins=list(range(START_PIN, END_PIN + 1)))

# Set up the shared analog inputs
cur_adc = Analog(servo2040.SHARED_ADC, servo2040.CURRENT_GAIN,
                 servo2040.SHUNT_RESISTOR, servo2040.CURRENT_OFFSET)

# Set up the analog multiplexer, including the pin for controlling pull-up/pull-down
mux = AnalogMux(servo2040.ADC_ADDR_0, servo2040.ADC_ADDR_1, servo2040.ADC_ADDR_2,
                muxed_pin=Pin(servo2040.SHARED_ADC))

# Create the LED bar, using PIO 1 and State Machine 0
led_bar = WS2812(servo2040.NUM_LEDS, 1, 0, servo2040.LED_DAT)

# Start updating the LED bar
led_bar.start()

# Enable all servos (this puts them at the middle).
# The servos are not going to be moved, but are activated to give a current draw
servos.enable_all()

# Read sensors until the user button is pressed
while user_sw.raw() is not True:

    # Select the current sense
    mux.select(servo2040.CURRENT_SENSE_ADDR)

    # Read the current sense several times and average the result
    current = 0
    for i in range(SAMPLES):
        current += cur_adc.read_current()
        time.sleep(TIME_BETWEEN)
    current /= SAMPLES

    # Print out the current sense value
    print("Current =", round(current, 4))

    # Convert the current to a percentage of the maximum we want to show
    percent = (current / MAX_CURRENT)

    # Update all the LEDs
    for i in range(servo2040.NUM_LEDS):
        # Calculate the LED's hue, with Red for high currents and green for low
        hue = (1.0 - i / (servo2040.NUM_LEDS - 1)) * 0.333

        # Calculate the current level the LED represents
        level = (i + 0.5) / servo2040.NUM_LEDS
        # If the percent is above the level, light the LED, otherwise turn it off
        if percent >= level:
            led_bar.set_hsv(i, hue, 1.0, BRIGHTNESS)
        else:
            led_bar.set_hsv(i, hue, 1.0, 0.0)

# Disable the servos
servos.disable_all()

# Turn off the LED bar
led_bar.clear()
