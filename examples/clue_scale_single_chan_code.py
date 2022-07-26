# SPDX-FileCopyrightText: 2021, 2022 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# clue_scale_single_chan_code.py  2022-07-26 1.2.0  Cedar Grove Maker Studios

# Clue Scale -- single channel version
# Cedar Grove NAU7802 FeatherWing example

# import clue_scale_single_calibrate  # uncomment to run calibration method for both channels

import time
import board
from simpleio import map_range
from adafruit_clue import clue
from adafruit_display_shapes.circle import Circle
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
import displayio
from cedargrove_nau7802 import NAU7802

clue.pixel[0] = (32, 32, 0)  # Set status indicator to yellow (initializing)

MAX_GR = 100  # Maximum (full-scale) display range in grams
DEFAULT_GAIN = 128  # Default gain for internal PGA
SAMPLE_AVG = 100  # Number of sample values to average
SCALE_NAME_1 = "COFFEE"  # 6 characters maximum
SCALE_NAME_2 = "SCALE"  # 6 characters maximum

min_gr = (MAX_GR // 5) * -1  # Calculated minimum display value

# Unique load cell calibration ratio; reference_weight_grams / raw_reading
# Obtained emperically for each individual load cell
# ###### FYI: A US dime coin weighs 2.268 ounces or x grams
# 100g at gain x128 for load cell serial#4540-02 attached to chan 1
CALIB_RATIO_1 = 100 / 215300

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

# Define the graphic for the zeroing button
zero_button_circle = Circle(14, 152, 14, fill=None, outline=clue.RED, stroke=2)
scale_group.append(zero_button_circle)

zero_button_label = Label(FONT_1, text="Z", color=clue.RED)
zero_button_label.x = 8
zero_button_label.y = 150
scale_group.append(zero_button_label)

# Place the minimum and maximum grams value labels next to the graduated scale
zero_value = Label(FONT_2, text="0", color=clue.CYAN)
zero_value.anchor_point = (1.0, 0.5)
zero_value.anchored_position = (97, 200)
scale_group.append(zero_value)

min_value = Label(FONT_2, text=str(min_gr), color=clue.CYAN)
min_value.anchor_point = (1.0, 1.0)
min_value.anchored_position = (99, 239)
scale_group.append(min_value)

max_value = Label(FONT_2, text=str(MAX_GR), color=clue.CYAN)
max_value.anchor_point = (1.0, 0)
max_value.anchored_position = (99, 0)
scale_group.append(max_value)

# Place the remaining four tick mark labels next to the graduated scale
plus_1_value = Label(FONT_2, text=str(1 * (MAX_GR // 5)), color=clue.CYAN)
plus_1_value.anchor_point = (1.0, 0.5)
plus_1_value.anchored_position = (99, 160)
scale_group.append(plus_1_value)

plus_2_value = Label(FONT_2, text=str(2 * (MAX_GR // 5)), color=clue.CYAN)
plus_2_value.anchor_point = (1.0, 0.5)
plus_2_value.anchored_position = (99, 120)
scale_group.append(plus_2_value)

plus_3_value = Label(FONT_2, text=str(3 * (MAX_GR // 5)), color=clue.CYAN)
plus_3_value.anchor_point = (1.0, 0.5)
plus_3_value.anchored_position = (99, 80)
scale_group.append(plus_3_value)

plus_4_value = Label(FONT_2, text=str(4 * (MAX_GR // 5)), color=clue.CYAN)
plus_4_value.anchor_point = (1.0, 0.5)
plus_4_value.anchored_position = (99, 40)
scale_group.append(plus_4_value)

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
    # Initiate internal calibration and zero the current channel
    # Use after power-up, a new channel is selected, or to adjust for drift
    # Can be used to zero the scale with tare weight
    nau7802.calibrate("INTERNAL")
    nau7802.calibrate("OFFSET")
    return


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

### Main loop: Read sample, move bubble, and display values
while True:
    clue.pixel[0] = (0, 32, 0)  # Set status indicator to green (ready)
    # Read the raw scale value and scale for grams and ounces
    value = read(SAMPLE_AVG)
    mass_grams = round(value * CALIB_RATIO_1, 1)
    mass_ounces = round(mass_grams * 0.03527, 2)
    grams_value.text = f"{mass_grams:5.1f}"
    ounces_value.text = f"{mass_ounces:5.2f}"

    bubble.y = int(map_range(mass_grams, min_gr, MAX_GR, 240, 0)) - 10
    if mass_grams > MAX_GR or mass_grams < min_gr:
        bubble.fill = clue.RED
    else:
        bubble.fill = None

    print(f" {mass_grams:5.1f} grams   {mass_ounces:5.2f} ounces")

    if clue.button_a:
        # Zero and recalibrate the NAU780
        clue.play_tone(1660, 0.3)  # Play "button pressed" tone
        clue.pixel[0] = (32, 0, 0)  # Set status indicator to red (stopped)
        bubble.fill = clue.RED  # Set bubble center to red (stopped)
        zero_scale()
        while clue.button_a:
            # Wait until button is released
            time.sleep(0.1)
        bubble.fill = None  # Set bubble center to transparent (ready)
        clue.play_tone(1440, 0.5)  # Play "reset completed" tone
