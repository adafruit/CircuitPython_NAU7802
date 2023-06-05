# SPDX-FileCopyrightText: 2023 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

"""
nau7802_async_simpletest.py  2023-01-13 2.0.2  Cedar Grove Maker Studios

Instantiates two NAU7802 channels with default gain of 128 and sample
average count of 2.
"""

import time
import board
import asyncio
from cedargrove_nau7802_async import NAU7802

# Instantiate 24-bit load sensor ADC; two channels, default gain of 128
nau7802 = NAU7802(board.I2C(), address=0x2A, active_channels=2)


def zero_channel(channel: int = 1):
    """Initiate internal calibration for current channel.Use when scale is started,
    a new channel is selected, or to adjust for measurement drift. Remove weight
    and tare from load cell before executing."""
    nau7802.channel = channel

    print(
        "channel %1d calibrate.INTERNAL: %5s"
        % (nau7802.channel, nau7802.calibrate_async("INTERNAL"))
    )
    print(
        "channel %1d calibrate.OFFSET:   %5s"
        % (nau7802.channel, nau7802.calibrate_async("OFFSET"))
    )
    print("...channel %1d zeroed" % nau7802.channel)


async def read_raw_value(channel: int = 1, samples=2):
    """Read and average consecutive raw sample values. Return average raw value."""
    sample_sum = 0
    sample_count = samples
    while sample_count > 0:
        while not nau7802.available():
            await asyncio.sleep(0)  # Let us play nice with anything else async
            pass
        sample_sum = sample_sum + nau7802.read()
        sample_count -= 1
    return int(sample_sum / samples)


async def simple_test():
    # Instantiate and calibrate load cell inputs
    print("*** Instantiate and calibrate load cells")
    # Enable NAU7802 digital and analog power
    enabled = await nau7802.enable_async(True)
    print("Digital and analog power enabled:", enabled)

    print("REMOVE WEIGHTS FROM LOAD CELLS")
    time.sleep(3)

    await zero_channel(1)  # Calibrate and zero channel
    await zero_channel(2)  # Calibrate and zero channel

    print("READY")

    ### Main loop: Read load cells and display raw values
    while True:
        print("=====")
        value = await read_raw_value(1)
        print("channel %1.0f raw value: %7.0f" % (nau7802.channel, value))

        value = await read_raw_value(2)
        print("channel %1.0f raw value: %7.0f" % (nau7802.channel, value))


asyncio.run(simple_test())
