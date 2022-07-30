# SPDX-FileCopyrightText: 2021, 2022 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT
#
# dual_clue_scale_mux_calibrator.py
# 2022-07-29 v1.1.0
#
# Clue Scale - Dual NAU7802 Sensor with TCA9548A Multiplexer Calibrator
# Adafruit NAU7802 Stemma breakout board example

import time
import board
import adafruit_tca9548a
from adafruit_clue import clue
from cedargrove_nau7802 import NAU7802

clue.pixel.brightness = 0.2  # Set NeoPixel brightness
clue.pixel[0] = clue.YELLOW  # Set status indicator to yellow (initializing)

SAMPLE_AVG = 500  # Number of sample values to average
DEFAULT_GAIN = 128  # Default gain for internal PGA

"""Instantiate 24-bit load sensor ADC boards attached to the TCA9845A I2C
multiplexer's channel 0 (sensor 1) and channel 1 (sensor2)."""
mux = adafruit_tca9548a.TCA9548A(board.I2C())
nau7802_1 = NAU7802(mux[0], address=0x2A, active_channels=1)
nau7802_2 = NAU7802(mux[1], address=0x2A, active_channels=1)


def zero_sensor(sensor=1):
    """Initiate internal calibration and zero the current channel of the
    specified sensor. Use after power-up, a new channel is selected, or to
    adjust for measurement drift.
    Can be used to zero the scale with a tare weight."""
    if sensor == 1:
        nau7802_1.calibrate("INTERNAL")
        nau7802_1.calibrate("OFFSET")
    elif sensor == 2:
        nau7802_2.calibrate("INTERNAL")
        nau7802_2.calibrate("OFFSET")


def read(sensor=1, samples=100):
    # Read and average consecutive raw sample values; return average raw value
    sample_sum = 0
    sample_count = samples
    while sample_count > 0:
        if sensor == 1:
            if nau7802_1.available:
                sample_sum = sample_sum + nau7802_1.read()
                sample_count -= 1
        elif sensor == 2:
            if nau7802_2.available:
                sample_sum = sample_sum + nau7802_2.read()
                sample_count -= 1
    return int(sample_sum / samples)


# Activate the NAU780 internal analog circuitry, set gain, and calibrate/zero
nau7802_1.enable(True)
nau7802_1.gain = DEFAULT_GAIN
nau7802_1.channel = 1
zero_sensor(1)

nau7802_2.enable(True)
nau7802_2.gain = DEFAULT_GAIN
nau7802_2.channel = 1
zero_sensor(2)

print("-----------------------------------")
print(" NAU7802 DUAL CHANNEL CALIBRATOR")
print("-----------------------------------")
print("Place a calibration weight on each")
print("load cell.")
print("To re-zero the load cells, remove")
print("any weights then press and hold A.")
print("-----------------------------------")
print("")

# Play "welcome" tones
clue.play_tone(1660, 0.15)
clue.play_tone(1440, 0.15)

# Main loop: Read samples and display values
while True:
    clue.pixel[0] = clue.GREEN  # Set status indicator to green

    # Read the raw value; print raw value, gain setting, and % of full-scale
    value = read(sensor=1, samples=SAMPLE_AVG)
    print(f"SENSOR_1 RAW VALUE: {value:7.0f}")
    print(f"GAIN: x{DEFAULT_GAIN}  full-scale: {(value / ((2**23) - 1)) * 100:3.2f}%")
    print("===================================")

    value = read(sensor=2, samples=SAMPLE_AVG)
    print(f"SENSOR_2 RAW VALUE: {value:7.0f}")
    print(f"GAIN: x{DEFAULT_GAIN}  full-scale: {(value / ((2**23) - 1)) * 100:3.2f}%")
    print("===================================")

    time.sleep(0.1)

    if clue.button_a:
        # Zero and recalibrate both sensors
        clue.play_tone(1660, 0.3)  # Play "button pressed" tone
        clue.pixel[0] = clue.RED  # Set status indicator to red (stopped)
        zero_sensor(1)
        zero_sensor(2)
        while clue.button_a:
            # Wait until button is released
            time.sleep(0.1)
        print("RECALIBRATED")
        clue.play_tone(1440, 0.5)  # Play "reset completed" tone
