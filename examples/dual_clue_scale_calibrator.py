# SPDX-FileCopyrightText: 2021, 2022 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT
#
# dual_clue_scale_calibrator.py
# 2022-07-27 v1.1.0
#
# Clue Scale Calibrator - Dual Channel Version
# Cedar Grove NAU7802 FeatherWing example

import time
import board
from adafruit_clue import clue
from cedargrove_nau7802 import NAU7802

clue.pixel[0] = 0x202000  # Set status indicator to yellow (initializing)

SAMPLE_AVG = 1000  # Number of sample values to average
DEFAULT_GAIN = 128  # Default gain for internal PGA

# Instantiate 24-bit load sensor ADC
nau7802 = NAU7802(board.I2C(), address=0x2A, active_channels=2)


def zero_channel():
    """Initiate internal calibration and zero the current channel. Use after
    power-up, a new channel is selected, or to adjust for measurement drift.
    Can be used to zero the scale with a tare weight."""
    nau7802.calibrate("INTERNAL")
    nau7802.calibrate("OFFSET")


def read(samples=100):
    # Read and average consecutive raw sample values; return average raw value
    sample_sum = 0
    sample_count = samples
    while sample_count > 0:
        if nau7802.available:
            sample_sum = sample_sum + nau7802.read()
            sample_count -= 1
    return int(sample_sum / samples)


# Activate the NAU780 internal analog circuitry, set gain, and calibrate/zero
nau7802.enable(True)
nau7802.gain = DEFAULT_GAIN  # Use default gain
nau7802.channel = 1
zero_channel()  # Calibrate and zero
nau7802.channel = 2
zero_channel()  # Calibrate and zero

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
    clue.pixel[0] = 0x002000  # Set status indicator to green

    # Read the raw value; print raw value, gain setting, and % of full-scale
    nau7802.channel = 1
    value = read(SAMPLE_AVG)
    print(f"CHAN_{nau7802.channel:1.0f} RAW VALUE: {value:7.0f}")
    print(f"GAIN: x{DEFAULT_GAIN}  full-scale: {(value / ((2**23) - 1)) * 100:3.2f}%")
    print("===================================")

    nau7802.channel = 2
    value = read(SAMPLE_AVG)
    print(f"CHAN_{nau7802.channel:1.0f} RAW VALUE: {value:7.0f}")
    print(f"GAIN: x{DEFAULT_GAIN}  full-scale: {(value / ((2**23) - 1)) * 100:3.2f}%")
    print("===================================")

    time.sleep(0.1)

    if clue.button_a:
        # Zero and recalibrate both channels
        clue.play_tone(1660, 0.3)  # Play "button pressed" tone
        clue.pixel[0] = 0x200000  # Set status indicator to red (stopped)
        nau7802.channel = 1
        zero_channel()
        nau7802.channel = 2
        zero_channel()
        while clue.button_a:
            # Wait until button is released
            time.sleep(0.1)
        print("RECALIBRATED")
        clue.play_tone(1440, 0.5)  # Play "reset completed" tone
