# SPDX-FileCopyrightText: 2023 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

"""
nau7802_async_simpletest.py  2023-01-13 2.0.2  Cedar Grove Maker Studios

Instantiates two NAU7802 channels with default gain of 128 and sample
average count of 2.
"""

import time
import datetime
import asyncio
import board
from cedargrove_nau7802_async import NAU7802


def zero_channel(nau7802: NAU7802, channel: int = 1):
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


async def read_raw_value(nau7802: NAU7802, channel: int):
    """Read an averaged value from average a given channel.  Use a larger number
    of samples to show how it interacts with other async methods.."""
    nau7802.channel = channel
    return await nau7802.read_async(samples=10)


async def simple_test():
    # Instantiate and calibrate load cell inputs
    print("*** Instantiate and calibrate load cells")
    nau7802 = await NAU7802.create_async(board.I2C(), address=0x2A, active_channels=2)

    print("REMOVE WEIGHTS FROM LOAD CELLS")
    time.sleep(3)

    await zero_channel(nau7802, 1)  # Calibrate and zero channel
    await zero_channel(nau7802, 2)  # Calibrate and zero channel

    print("READY")

    ### Main loop: Read load cells and display raw values
    while True:
        print("=====")
        value = await read_raw_value(nau7802, 1)
        print("channel %1.0f raw value: %7.0f" % (nau7802.channel, value))

        value = await read_raw_value(nau7802, 2)
        print("channel %1.0f raw value: %7.0f" % (nau7802.channel, value))


async def clock():
    while True:
        print("{}: tick".format(datetime.datetime.now()))
        await asyncio.sleep(1)
        print("{}: tock".format(datetime.datetime.now()))
        await asyncio.sleep(1)


async def main():
    # Run a loop that prints current scale values in parallel with a method a
    # ticking clock to show that they interleave.
    await asyncio.gather(
        simple_test(),
        clock(),
    )


asyncio.run(simple_test())
