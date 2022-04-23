Introduction
============




.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/CedarGroveStudios/Cedargrove_CircuitPython_NAU7802/workflows/Build%20CI/badge.svg
    :target: https://github.com/CedarGroveStudios/Cedargrove_CircuitPython_NAU7802/actions
    :alt: Build Status


.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

A CircuitPython driver class for the NAU7802 24-bit ADC.


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Bus Device <https://github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_
* `Register <https://github.com/adafruit/Adafruit_CircuitPython_Register>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install nau7802

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

```python
import board
from cedargrove_nau7802 import NAU7802

# Instantiate NAU7802 ADC
nau7802 = NAU7802(board.I2C(), address=0x2A, active_channels=2)
```

Other examples can be found in the `examples` folder.

.. todo:: other examples should live in the
examples folder and be included in docs/examples.rst.

Documentation
=============
API documentation for this library can be found on [NAU7802 CircuitPython Driver: Class Description](https://github.com/CedarGroveStudios/NAU7802_24-bit_ADC_FeatherWing/blob/main/docs/pseudo%20readthedocs%20cedargrove_nau7802.pdf)

<a href="https://oshpark.com/shared_projects/qFvEU3Bn"><img src="https://oshpark.com/packs/media/images/badge-5f4e3bf4bf68f72ff88bd92e0089e9cf.png" alt="Order from OSH Park"></img></a>

NAU7802 FeatherWing  16-DIP (THT) Version:

<a href="https://oshpark.com/shared_projects/ZfryHYnc"><img src="https://oshpark.com/packs/media/images/badge-5f4e3bf4bf68f72ff88bd92e0089e9cf.png" alt="Order from OSH Park"></img></a>


![NAU7802 FeatherWing](https://github.com/CedarGroveStudios/NAU7802_24-bit_ADC_FeatherWing/blob/main/graphics/glamor_shot.jpeg)

![NAU7802 FeatherWing pinout](https://github.com/CedarGroveStudios/NAU7802_24-bit_ADC_FeatherWing/blob/main/docs/NAU7802_pinout_wht_lores.png)

![NAU7802 cable pinout](https://github.com/CedarGroveStudios/NAU7802_24-bit_ADC_FeatherWing/blob/main/docs/NAU7802_pinout_wht_p2.png)

![Clue_Scale](https://github.com/CedarGroveStudios/NAU7802_24-bit_ADC_FeatherWing/blob/main/graphics/Clue_Scale_2020-11-25_trim.png)

Needing a calibration weight? The U.S. Mint coin specifications might have some information that could help -- if you have some spare change. https://www.usmint.gov/learn/coin-and-medal-programs/coin-specifications


Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/CedarGroveStudios/Cedargrove_CircuitPython_NAU7802/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
