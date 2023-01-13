# SPDX-FileCopyrightText: 2021, 2022 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT
#
# dual_clue_scale_code.py
# 2022-07-29 v1.2.0
#
# Clue Scale - Dual Channel Version
# Cedar Grove NAU7802 FeatherWing example

# import dual_clue_scale_calibrator  # Uncomment to run calibrator method
import time
import board
from simpleio import map_range
from adafruit_clue import clue
from adafruit_display_shapes.circle import Circle
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
import displayio
from cedargrove_nau7802 import NAU7802

clue.pixel.brightness = 0.2  # Set NeoPixel brightness
clue.pixel[0] = clue.YELLOW  # Set status indicator to yellow (initializing)

MAX_GR = 100  # Maximum (full-scale) display range in grams
DEFAULT_GAIN = 128  # Default gain for internal PGA
SAMPLE_AVG = 100  # Number of sample values to average
CHAN_1_LABEL = "SHOT"  # 6 characters maximum
CHAN_2_LABEL = "BEANS"  # 6 characters maximum

"""Enter the calibration ratio for the individual load cell in-use. The ratio is
composed of the reference weight in grams divided by the raw reading. For
example, a raw reading of 215300 for a 100 gram weight results in a calibration
ratio of 100 / 215300. Use the clue_scale_single_calibrate method to obtain the
raw value.
FYI: A US dime coin weighs 2.268 grams or 0.079 ounces."""
CALIB_RATIO_1 = 100 / 215300  # load cell serial#4540-01 attached to chan 1
CALIB_RATIO_2 = 100 / 215300  # load cell serial#4540-02 attached to chan 2

# Instantiate 24-bit load sensor ADC
nau7802 = NAU7802(board.I2C(), address=0x2A, active_channels=2)

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

chan_1_name = Label(FONT_1, text=CHAN_1_LABEL, color=clue.CYAN)
chan_1_name.anchor_point = (0.5, 0.5)
chan_1_name.anchored_position = (40, 96)
scale_group.append(chan_1_name)

chan_2_name = Label(FONT_1, text=CHAN_2_LABEL, color=clue.CYAN)
chan_2_name.anchor_point = (0.5, 0.5)
chan_2_name.anchored_position = (199, 96)
scale_group.append(chan_2_name)

# Define the graphics for the zeroing buttons
zero_1_button_circle = Circle(14, 152, 14, fill=None, outline=clue.RED, stroke=2)
scale_group.append(zero_1_button_circle)

zero_1_button_label = Label(FONT_1, text="Z", color=clue.RED)
zero_1_button_label.x = 8
zero_1_button_label.y = 150
scale_group.append(zero_1_button_label)

zero_2_button_circle = Circle(225, 152, 14, fill=None, outline=clue.RED, stroke=2)
scale_group.append(zero_2_button_circle)

zero_2_button_label = Label(FONT_1, text="Z", color=clue.RED)
zero_2_button_label.x = 219
zero_2_button_label.y = 150
scale_group.append(zero_2_button_label)

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

# Place the weight units and values near the bottom of the display
chan_1_name = Label(FONT_0, text="grams", color=clue.BLUE)
chan_1_name.anchor_point = (1.0, 0)
chan_1_name.anchored_position = (80, 216)
scale_group.append(chan_1_name)

chan_2_name = Label(FONT_0, text="grams", color=clue.BLUE)
chan_2_name.anchor_point = (1.0, 0)
chan_2_name.anchored_position = (230, 216)
scale_group.append(chan_2_name)

chan_1_value = Label(FONT_0, text="0.0", color=clue.WHITE)
chan_1_value.anchor_point = (1.0, 0.5)
chan_1_value.anchored_position = (80, 200)
scale_group.append(chan_1_value)

chan_2_value = Label(FONT_0, text="0.0", color=clue.WHITE)
chan_2_value.anchor_point = (1.0, 0.5)
chan_2_value.anchored_position = (230, 200)
scale_group.append(chan_2_value)

# Define the moveable indicator bubbles
indicator_group = displayio.Group()
chan_1_bubble = Circle(112, 200, 8, fill=clue.YELLOW, outline=clue.YELLOW, stroke=3)
indicator_group.append(chan_1_bubble)

chan_2_bubble = Circle(131, 200, 8, fill=clue.GREEN, outline=clue.GREEN, stroke=3)
indicator_group.append(chan_2_bubble)

scale_group.append(indicator_group)
display.show(scale_group)


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
        if nau7802.available():
            sample_sum = sample_sum + nau7802.read()
            sample_count -= 1
    return int(sample_sum / samples)


# Activate the NAU780 internal analog circuitry, set gain, and calibrate/zero
nau7802.enable(True)
nau7802.gain = DEFAULT_GAIN
nau7802.channel = 1
zero_channel()
nau7802.channel = 2
zero_channel()

# Play "welcome" tones
clue.play_tone(1660, 0.15)
clue.play_tone(1440, 0.15)

# Main loop: Read samples, move bubbles, and display values
while True:
    clue.pixel[0] = clue.GREEN  # Set status indicator to green (ready)

    nau7802.channel = 1
    value = read(SAMPLE_AVG)
    chan_1_mass_gr = round(value * CALIB_RATIO_1, 1)
    chan_1_mass_oz = round(chan_1_mass_gr * 0.03527, 2)
    chan_1_value.text = f"{chan_1_mass_gr:5.1f}"

    min_gr = (MAX_GR // 5) * -1  # Minimum display value
    chan_1_bubble.y = int(map_range(chan_1_mass_gr, min_gr, MAX_GR, 240, 0)) - 8
    if chan_1_mass_gr > MAX_GR or chan_1_mass_gr < min_gr:
        chan_1_bubble.fill = clue.RED
    else:
        chan_1_bubble.fill = None

    nau7802.channel = 2
    value = read(SAMPLE_AVG)
    chan_2_mass_gr = round(value * CALIB_RATIO_2, 1)
    chan_2_mass_oz = round(chan_2_mass_gr * 0.03527, 2)
    chan_2_value.text = f"{chan_2_mass_gr:5.1f}"

    chan_2_bubble.y = int(map_range(chan_2_mass_gr, min_gr, MAX_GR, 240, 0)) - 8
    if chan_2_mass_gr > MAX_GR or chan_2_mass_gr < min_gr:
        chan_2_bubble.fill = clue.RED
    else:
        chan_2_bubble.fill = None

    print(f"chan_1:{chan_1_mass_gr:5.1f} gr  chan_2:{chan_2_mass_gr:5.1f} gr")

    if clue.button_a:
        # Zero and recalibrate channel 1
        clue.pixel[0] = clue.RED  # Set status indicator to red (stopped)
        chan_1_bubble.fill = clue.RED
        clue.play_tone(1660, 0.3)  # Play "button pressed" tone

        nau7802.channel = 1
        zero_channel()

        while clue.button_a:
            # Wait until button is released
            time.sleep(0.1)

        clue.play_tone(1440, 0.5)  # Play "reset completed" tone
        chan_1_bubble.fill = None

    if clue.button_b:
        # Zero and recalibrate channel 2
        clue.pixel[0] = clue.RED  # Set status indicator to red (stopped)
        chan_2_bubble.fill = clue.RED
        clue.play_tone(1660, 0.3)  # Play "button pressed" tone

        nau7802.channel = 2
        zero_channel()

        while clue.button_a:
            # Wait until button is released
            time.sleep(0.1)

        clue.play_tone(1440, 0.5)  # Play "reset completed" tone
        chan_2_bubble.fill = None
