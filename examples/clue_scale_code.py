# SPDX-FileCopyrightText: 2021, 2022 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# clue_scale_code.py  2022-04-23 1.1.0  Cedar Grove Maker Studios

# Clue Scale
# Cedar Grove NAU7802 FeatherWing example

# import clue_scale_calibrate  # uncomment to run calibration method
import time
import board
from simpleio import map_range
from adafruit_clue import clue
from adafruit_display_shapes.circle import Circle
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
import displayio
from cedargrove_nau7802 import NAU7802

clue.pixel[0] = (16, 0, 16)  # Set status indicator to purple during instantiation phase

DEFAULT_CHAN = 1  # Select load cell channel input; channel A=1, channel B=2
SAMPLE_AVG = 100  # Number of sample values to average
MAX_GR = 100  # Maximum (full-scale) display range in grams
MIN_GR = (MAX_GR // 5) * -1  # Calculated minimum display value
DEFAULT_GAIN = 128  # Default gain for internal PGA

# Load cell dime-weight calibration ratio; 2.268 gm / ADC_raw_measurement
# Obtained emperically; individual load cell dependent
CALIB_RATIO = 100 / 215300  # 100g at gain x128 for load cell serial#4540-02

# Instantiate 24-bit load sensor ADC
nau7802 = NAU7802(board.I2C(), address=0x2A, active_channels=2)

# Instantiate display and fonts
print("*** Instantiate the display and fonts")
display = board.DISPLAY
scale_group = displayio.Group(max_size=21)

FONT_0 = bitmap_font.load_font("/fonts/Helvetica-Bold-24.bdf")
FONT_1 = bitmap_font.load_font("/fonts/OpenSans-16.bdf")
FONT_2 = bitmap_font.load_font("/fonts/OpenSans-9.bdf")

# Define displayio background and group elements
print("*** Define displayio background and group elements")
bkg = displayio.OnDiskBitmap("/clue_scale_dual_chan_bkg.bmp")
_background = displayio.TileGrid(bkg, pixel_shader=bkg.pixel_shader, x=0, y=0)
scale_group.append(_background)

tare_button_label = Label(FONT_1, text="T", color=clue.CYAN, max_glyphs=1)
tare_button_label.x = 8
tare_button_label.y = 160
scale_group.append(tare_button_label)

zero_button_label = Label(FONT_1, text="Z", color=clue.RED, max_glyphs=1)
zero_button_label.x = 219
zero_button_label.y = 160
scale_group.append(zero_button_label)

tare_button_circle = Circle(14, 159, 14, fill=None, outline=clue.CYAN, stroke=2)
scale_group.append(tare_button_circle)

zero_button_circle = Circle(225, 159, 14, fill=None, outline=clue.RED, stroke=2)
scale_group.append(zero_button_circle)

zero_value = Label(FONT_2, text="0", color=clue.CYAN, max_glyphs=1)
zero_value.anchor_point = (1.0, 0.5)
zero_value.anchored_position = (105, 200)
scale_group.append(zero_value)

min_value = Label(FONT_2, text=str(MIN_GR), color=clue.CYAN, max_glyphs=6)
min_value.anchor_point = (1.0, 1.0)
min_value.anchored_position = (105, 239)
scale_group.append(min_value)

max_value = Label(FONT_2, text=str(MAX_GR), color=clue.CYAN, max_glyphs=6)
max_value.anchor_point = (1.0, 0)
max_value.anchored_position = (105, 0)
scale_group.append(max_value)

plus_1_value = Label(FONT_2, text=str(1 * (MAX_GR // 5)), color=clue.CYAN, max_glyphs=6)
plus_1_value.anchor_point = (1.0, 0.5)
plus_1_value.anchored_position = (105, 160)
scale_group.append(plus_1_value)

plus_2_value = Label(FONT_2, text=str(2 * (MAX_GR // 5)), color=clue.CYAN, max_glyphs=6)
plus_2_value.anchor_point = (1.0, 0.5)
plus_2_value.anchored_position = (105, 120)
scale_group.append(plus_2_value)

plus_3_value = Label(FONT_2, text=str(3 * (MAX_GR // 5)), color=clue.CYAN, max_glyphs=6)
plus_3_value.anchor_point = (1.0, 0.5)
plus_3_value.anchored_position = (105, 80)
scale_group.append(plus_3_value)

plus_4_value = Label(FONT_2, text=str(4 * (MAX_GR // 5)), color=clue.CYAN, max_glyphs=6)
plus_4_value.anchor_point = (1.0, 0.5)
plus_4_value.anchored_position = (105, 40)
scale_group.append(plus_4_value)

grams_label = Label(FONT_0, text="grams", color=clue.BLUE, max_glyphs=6)
grams_label.anchor_point = (1.0, 0)
grams_label.anchored_position = (90, 216)
scale_group.append(grams_label)

ounces_label = Label(FONT_0, text="ounces", color=clue.BLUE, max_glyphs=6)
ounces_label.anchor_point = (1.0, 0)
ounces_label.anchored_position = (230, 216)
scale_group.append(ounces_label)

mass_gr_value = Label(FONT_0, text="0.00", color=clue.WHITE, max_glyphs=10)
mass_gr_value.anchor_point = (1.0, 0.5)
mass_gr_value.anchored_position = (90, 200)
scale_group.append(mass_gr_value)

mass_oz_value = Label(FONT_0, text="0.000", color=clue.WHITE, max_glyphs=10)
mass_oz_value.anchor_point = (1.0, 0.5)
mass_oz_value.anchored_position = (230, 200)
scale_group.append(mass_oz_value)

tare_gr_label = Label(FONT_1, text="tare", color=clue.BLUE, max_glyphs=4)
tare_gr_label.anchor_point = (1.0, 0.5)
tare_gr_label.anchored_position = (80, 114)
scale_group.append(tare_gr_label)

tare_gr_value = Label(FONT_1, text="0.00", color=clue.CYAN, max_glyphs=10)
tare_gr_value.anchor_point = (1.0, 0.5)
tare_gr_value.anchored_position = (84, 94)
scale_group.append(tare_gr_value)

tare_oz_label = Label(FONT_1, text="tare", color=clue.BLUE, max_glyphs=4)
tare_oz_label.anchor_point = (1.0, 0.5)
tare_oz_label.anchored_position = (224, 114)
scale_group.append(tare_oz_label)

tare_oz_value = Label(FONT_1, text="0.000", color=clue.CYAN, max_glyphs=10)
tare_oz_value.anchor_point = (1.0, 0.5)
tare_oz_value.anchored_position = (224, 94)
scale_group.append(tare_oz_value)

# Define moveable bubble
indicator_group = displayio.Group(max_size=1)
indicator_bubble = Circle(120, 200, 8, fill=clue.YELLOW, outline=clue.YELLOW, stroke=3)
indicator_group.append(indicator_bubble)

scale_group.append(indicator_group)
display.show(scale_group)


def zero_channel():
    # Initiate internal calibration for current channel; return raw zero offset value
    # Use when scale is started, a new channel is selected, or to adjust for measurement drift
    # Remove weight and tare from load cell before executing
    print(
        "channel %1d calibrate.INTERNAL: %5s"
        % (nau7802.channel, nau7802.calibrate("INTERNAL"))
    )
    print(
        "channel %1d calibrate.OFFSET:   %5s"
        % (nau7802.channel, nau7802.calibrate("OFFSET"))
    )
    zero_offset = read(100)  # Read average of 100 samples to establish zero offset
    print("...channel zeroed")
    return zero_offset


def get_tare(new_tare=None):
    # Measure and store tare weight; return raw, grams, and ounces values
    if new_tare is None:
        # Read average of 100 samples and store raw tare offset
        tare_offset = read(100)
        tare_gr_value.color = clue.CYAN
        tare_gr_label.color = clue.BLUE
        tare_oz_value.color = clue.CYAN
        tare_oz_label.color = clue.BLUE
    else:
        # Set raw tare offset to zero and disable tare display
        tare_offset = 0
        tare_gr_value.color = clue.BLACK
        tare_gr_label.color = clue.BLACK
        tare_oz_value.color = clue.BLACK
        tare_oz_label.color = clue.BLACK
    tare_gr_offset = round(tare_offset * CALIB_RATIO, 3)
    tare_oz_offset = round(tare_gr_offset * 0.03527, 4)
    return tare_offset, tare_gr_offset, tare_oz_offset


def read(samples=100):
    # Read and average consecutive raw sample values; return average raw value
    sample_sum = 0
    sample_count = samples
    while sample_count > 0:
        if nau7802.available:
            sample_sum = sample_sum + nau7802.read()
            sample_count -= 1
    return int(sample_sum / samples)


# Instantiate and calibrate load cell inputs
print("*** Instantiate and calibrate load cells")
clue.pixel[0] = (16, 16, 0)  # Set status indicator to yellow
print("    enable NAU7802 digital and analog power: %5s" % (nau7802.enable(True)))

nau7802.gain = DEFAULT_GAIN  # Use default gain
nau7802.channel = DEFAULT_CHAN  # Set to default channel
zero = zero_channel()  # Calibrate and get raw zero offset value
tare, tare_gr, tare_oz = get_tare(0)  # Disable tare subtraction and display
clue.pixel[0] = (0, 16, 0)  # Set status indicator to green
clue.play_tone(1660, 0.15)
clue.play_tone(1440, 0.15)

### Main loop: Read sample, move bubble, and display values
#     Monitor Zeroing and Tare buttons
while True:
    value = read(SAMPLE_AVG)
    mass_gr = round((value - zero - tare) * CALIB_RATIO, 1)
    mass_oz = round(mass_gr * 0.03527, 2)

    indicator_bubble.y = int(map_range(mass_gr, MIN_GR, MAX_GR, 240, 0)) - 8
    if mass_gr > MAX_GR or mass_gr < MIN_GR:
        indicator_bubble.fill = clue.RED
    else:
        indicator_bubble.fill = None

    mass_gr_value.text = "%5.1f" % (mass_gr)
    mass_oz_value.text = "%2.2f" % (mass_oz)
    tare_gr_value.text = "%6.1f" % (tare_gr)
    tare_oz_value.text = "%2.2f" % (tare_oz)

    print("(%+5.1f, %+2.2f)" % (mass_gr, mass_oz))
    # print('raw value:', value, hex(value))

    if clue.button_a:
        # Store tare value; click and release to tare; hold > 1 second to clear tare value
        clue.play_tone(1660, 0.3)
        clue.pixel[0] = (16, 16, 0)
        indicator_bubble.fill = clue.YELLOW
        time.sleep(1)
        if clue.button_a:
            clue.play_tone(1660, 0.3)
            tare, tare_gr, tare_oz = get_tare(0)
        else:
            tare, tare_gr, tare_oz = get_tare()
        while clue.button_a:
            time.sleep(0.1)
        indicator_bubble.fill = None
        clue.pixel[0] = (0, 16, 0)
        clue.play_tone(1440, 0.5)

    if clue.button_b:
        # Zero and recalibrate NAU7802 chip; clear tare value
        clue.play_tone(1660, 0.3)
        clue.pixel[0] = (16, 0, 0)
        indicator_bubble.fill = clue.RED
        zero = zero_channel()
        tare, tare_gr, tare_oz = get_tare(0)
        while clue.button_b:
            time.sleep(0.1)
        indicator_bubble.fill = None
        clue.pixel[0] = (0, 16, 0)
        clue.play_tone(1440, 0.5)
