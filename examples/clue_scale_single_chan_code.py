# SPDX-FileCopyrightText: 2021, 2022 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT
#
# clue_scale_single_chan_code.py  2022-07-26 1.2.0  Cedar Grove Maker Studios
#
# Clue Scale -- single channel version
# Cedar Grove NAU7802 FeatherWing example

# import clue_scale_single_calibrate  # uncomment to run calibration method

import time
import board
from simpleio import map_range
from adafruit_clue import clue
from adafruit_display_shapes.circle import Circle
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
import displayio
from cedargrove_nau7802 import NAU7802

clue.pixel[0] = 0x202000  # Set status indicator to yellow (initializing)

MAX_GR = 100  # Maximum (full-scale) display range in grams
DEFAULT_GAIN = 128  # Default gain for internal PGA
SAMPLE_AVG = 100  # Number of sample values to average
SCALE_NAME_1 = "COFFEE"  # 6 characters maximum
SCALE_NAME_2 = "SCALE"  # 6 characters maximum

min_gr = (MAX_GR // 5) * -1  # Calculated minimum display value

"""Enter the calibration ratio for the individual load cell in-use. The ratio is
composed of the reference weight in grams divided by the raw reading. For
example, a raw reading of 215300 for a 100 gram weight results in a calibration
ratio of 100 / 215300. Use the clue_scale_single_calibrate method to obtain the
raw value.
For referency, a US dime (10-cent) coin weighs 2.268 grams."""
CALIB_RATIO_1 = 100 / 215300  # load cell serial#4540-02

# Instantiate 24-bit load sensor ADC
nau7802 = NAU7802(board.I2C(), address=0x2A, active_channels=1)

# Instantiate display and fonts
display = board.DISPLAY
scale_group = displayio.Group()

FONT_0 = bitmap_font.load_font("/fonts/Helvetica-Bold-24.bdf")
FONT_1 = bitmap_font.load_font("/fonts/OpenSans-16.bdf")
FONT_2 = bitmap_font.load_font("/fonts/OpenSans-9.bdf")

# Define displayio background and group elements
bkg = displayio.OnDiskBitmap("/clue_scale_bkg.bmp")
_background = displayio.TileGrid(bkg, pixel_shader=bkg.pixel_shader, x=0, y=0)

scale_group.append(_background)

# Place the project name on either side of the graduated scale
scale_name_1 = Label(FONT_1, text=SCALE_NAME_1, color=clue.CYAN)
scale_name_1.anchor_point = (0.5, 0.5)
scale_name_1.anchored_position = (40, 96)
scale_group.append(scale_name_1)

scale_name_2 = Label(FONT_1, text=SCALE_NAME_2, color=clue.CYAN)
scale_name_2.anchor_point = (0.5, 0.5)
scale_name_2.anchored_position = (199, 96)
scale_group.append(scale_name_2)

# Define the zeroing button graphic
zero_button_circle = Circle(14, 152, 14, fill=None, outline=clue.RED, stroke=2)
scale_group.append(zero_button_circle)

zero_button_label = Label(FONT_1, text="Z", color=clue.RED)
zero_button_label.x = 8
zero_button_label.y = 150
scale_group.append(zero_button_label)

# Place tickmarks next to the graduated scale
for i in range(-1, 6):
    tick_value = Label(FONT_2, text=str((MAX_GR) // 5 * i), color=clue.CYAN)
    if i == -1:
        tick_value.anchor_point = (1.0, 1.1)
    elif i == 5:
        tick_value.anchor_point = (1.0, 0.0)
    else:
        tick_value.anchor_point = (1.0, 0.5)
    tick_value.anchored_position = (99, 201 - (i * 40))
    scale_group.append(tick_value)

# Place the grams and ounces labels and values near the bottom of the display
grams_label = Label(FONT_0, text="grams", color=clue.BLUE)
grams_label.anchor_point = (1.0, 0)
grams_label.anchored_position = (80, 216)
scale_group.append(grams_label)

ounces_label = Label(FONT_0, text="ounces", color=clue.BLUE)
ounces_label.anchor_point = (1.0, 0)
ounces_label.anchored_position = (230, 216)
scale_group.append(ounces_label)

grams_value = Label(FONT_0, text="0.0", color=clue.WHITE)
grams_value.anchor_point = (1.0, 0.5)
grams_value.anchored_position = (80, 200)
scale_group.append(grams_value)

ounces_value = Label(FONT_0, text="0.00", color=clue.WHITE)
ounces_value.anchor_point = (1.0, 0.5)
ounces_value.anchored_position = (230, 200)
scale_group.append(ounces_value)

# Define the moveable indicator bubble
indicator_group = displayio.Group()
bubble = Circle(120, 200, 10, fill=clue.YELLOW, outline=clue.YELLOW, stroke=3)
indicator_group.append(bubble)

scale_group.append(indicator_group)
display.show(scale_group)


def zero_scale():
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
nau7802.gain = DEFAULT_GAIN
zero_scale()

# Play "welcome" tones
clue.play_tone(1660, 0.15)
clue.play_tone(1440, 0.15)

# Main loop: Read sample, move bubble, and display values
while True:
    clue.pixel[0] = 0x002000  # Set status indicator to green (ready)

    # Read the raw scale value and scale for grams and ounces
    value = read(SAMPLE_AVG)
    mass_grams = round(value * CALIB_RATIO_1, 1)
    mass_ounces = round(mass_grams * 0.03527, 2)
    grams_value.text = f"{mass_grams:5.1f}"
    ounces_value.text = f"{mass_ounces:5.2f}"

    # Reposition the indicator bubble based on grams value
    bubble.y = int(map_range(mass_grams, min_gr, MAX_GR, 240, 0)) - 10
    if mass_grams > MAX_GR or mass_grams < min_gr:
        bubble.fill = clue.RED
    else:
        bubble.fill = None

    print(f" {mass_grams:5.1f} grams   {mass_ounces:5.2f} ounces")

    if clue.button_a:
        # Zero and recalibrate the NAU780
        clue.pixel[0] = 0x200000  # Set status indicator to red (stopped)
        bubble.fill = clue.RED  # Set bubble center to red (stopped)
        clue.play_tone(1660, 0.3)  # Play "button pressed" tone

        zero_scale()

        while clue.button_a:
            # Wait until button is released
            time.sleep(0.1)

        clue.play_tone(1440, 0.5)  # Play "reset completed" tone
        bubble.fill = None  # Set bubble center to transparent (ready)
