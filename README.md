# Aula F87 Pro CLI Controller

**DISCLAIMER: THIS PROJECT DOES NOT REVERSE ENGINEER THE COMPLETE COMMUNICATION PROTOCOL OF THE AULA F87 PRO KEYBOARD. IT IS A SIMPLE SCRIPT DESIGNED TO SEND RGB DATA TO THE KEYBOARD FOR LIGHTING CONTROL. CURRENTLY, THIS SCRIPT HAS NO CAPABILITY TO SAVE CONFIGURATIONS ON THE KEYBOARD ITSELF; ALL EFFECTS ARE APPLIED IN REAL-TIME VIA SOFTWARE.**

A command-line interface (CLI) tool to control the RGB lighting of the Aula F87 Pro keyboard on Linux.

## Limitations

*   **Wired Mode Only:** Currently, this tool has only been confirmed to work with the Aula F87 Pro keyboard when connected via a USB cable (wired mode). Efforts to control RGB lighting in wireless mode (e.g., 2.4GHz or Bluetooth) have so far been unsuccessful.

## Features

*   Set solid colors for all LEDs.
*   Apply a breathing light effect.
*   Turn off all keyboard lights.
*   Run a test sequence to check RGB functionality.
*   Automatically find and save the correct HID interface for RGB control.
*   Manage configuration via `~/.aula_f87_config.json`.
*   Parse color inputs in various formats (named colors, hex codes, RGB strings).
*   List available predefined color names.

## Typical Use Cases

1.   **Dynamic Desktop Color Sync:** Use this CLI tool as a backend for a separate script that monitors your desktop environment's dominant colors (e.g., from your wallpaper or active window). The external script can then call `aula-f87pro --color <detected_color>` to dynamically update your keyboard lighting to match your desktop theme.

2.   **Custom Lighting Effects:** While this tool provides basic effects like solid color and breathing, it can serve as a foundation for more complex custom lighting patterns. If the built-in effects aren't sufficient, you can create your own scripts that repeatedly call `aula-f87pro` with different color arguments in sequence or create new functions to generate unique animations. This will require some programming and tinkering on your part.

## Installation

1.  **Prerequisites:**
    *   Python 3.9 or higher
    *   `pip` (Python package installer)
    *   `libhidapi-hidraw0` (or equivalent for your distribution) for `hidapi` to work.
        ```bash
        sudo apt-get update
        sudo apt-get install libhidapi-hidraw0
        ```

2.  **Clone the repository (if you haven't already):**
    ```bash
    git clone https://github.com/Ahorts/aula-f87pro.git
    cd aula-f87pro
    ```

3.  **Install the CLI tool:**
    It's recommended to install in a virtual environment.
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install .
    ```
    Alternatively, for an editable install (changes in code are reflected immediately):
    ```bash
    pip install -e .
    ```

## Udev Rules for Non-Root Access

To use this tool without `sudo`, you need to set up udev rules to grant your user permission to access the keyboard's HID interface.

1.  Create a new udev rule file (replace nano with your editor of choice):
    ```bash
    sudo nano /etc/udev/rules.d/99-aula-f87pro.rules
    ```

2.  Add the following line to the file:
    ```
    SUBSYSTEM=="hidraw", ATTRS{idVendor}=="258a", ATTRS{idProduct}=="010c", MODE="0666"
    ```
    *Note: `MODE="0666"` grants access to all users. For a more secure setup, you can use `GROUP="plugdev"` (or another group your user belongs to) and `MODE="0660"`.*

3.  Save the file and exit the editor.

4.  Reload the udev rules and trigger them:
    ```bash
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    ```

5.  Unplug and replug your Aula F87 Pro keyboard.

## Usage

The primary command is `aula-f87pro`.

**First-time Setup (Finding the Interface):**
```bash
aula-f87pro --find-interface
```