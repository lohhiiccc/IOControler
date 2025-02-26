from Xlib import display, X, XK
from enum import Enum
import time

class Action(Enum):
    KEY_STROK = 1
    KEY_PRESS = 2
    KEY_RELEASE = 3
    KEY_SHORTCUT = 4
    MOUSE_MOVE = 5
    MOUSE_CLICK = 6
    MOUSE_PRESS = 7
    MOUSE_RELEASE = 8

class MouseButtons(Enum):
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3

class Controller:
    def __init__(self):
        self.d = display.Display()
        self.s = self.d.screen()
        self.root = self.s.root

    def key_stroke(self, key_name: str):
        keysym = XK.string_to_keysym(key_name)
        keycode = self.d.keysym_to_keycode(keysym)
        self.d.xtest_fake_input(X.KeyPress, keycode)
        self.d.xtest_fake_input(X.KeyRelease, keycode)
        self.d.sync()

    def key_press(self, key_name: str):
        keysym = XK.string_to_keysym(key_name)
        keycode = self.d.keysym_to_keycode(keysym)
        self.d.xtest_fake_input(X.KeyPress, keycode)
        self.d.sync()
    
    def key_release(self, key_name: str):
        keysym = XK.string_to_keysym(key_name)
        keycode = self.d.keysym_to_keycode(keysym)
        self.d.xtest_fake_input(X.KeyRelease, keycode)
        self.d.sync()

    def shortcut(self, keys: list):
        """
        Simulates a keyboard shortcut by pressing all keys in order and then releasing them in reverse order.
        :param keys: List of key names as strings, e.g., ["Control_L", "C"]
        """
        keycodes = []
        for key in keys:
            keysym = XK.string_to_keysym(key)
            keycode = self.d.keysym_to_keycode(keysym)
            if keycode == 0:
                raise Exception(f"Key not found: {key}")
            keycodes.append(keycode)

        # Press all keys in the order provided.
        for keycode in keycodes:
            self.d.xtest_fake_input(X.KeyPress, keycode)
        self.d.sync()

        # Optional delay can be added here (e.g., time.sleep(0.05))

        # Release keys in reverse order.
        for keycode in reversed(keycodes):
            self.d.xtest_fake_input(X.KeyRelease, keycode)
        self.d.sync()

    def mouse_move(self, x: int, y: int):
        """
        Moves the mouse pointer to the specified (x, y) screen coordinates using the root window's warp_pointer.
        """
        self.root.warp_pointer(x, y)
        self.d.sync()

    def mouse_click(self, button: int = 1):
        """
        Simulates a mouse click by sending a button press and release.
        :param button: Mouse button number (1 for left, 2 for middle, 3 for right)
        """
        self.d.xtest_fake_input(X.ButtonPress, button)
        self.d.sync()
        time.sleep(0.05)  # Short delay to mimic a real click
        self.d.xtest_fake_input(X.ButtonRelease, button)
        self.d.sync()

    def mouse_click(self, button: MouseButtons = MouseButtons.LEFT):
        self.d.xtest_fake_input(X.ButtonPress, button.value)
        self.d.sync()
        time.sleep(0.05)  # Short delay to mimic a real click
        self.d.xtest_fake_input(X.ButtonRelease, button.value)
        self.d.sync()

    def mouse_press(self, button: int = 1):
        """
        Simulates pressing (without releasing) a mouse button.
        """
        self.d.xtest_fake_input(X.ButtonPress, button)
        self.d.sync()

    def mouse_press(self, button: MouseButtons = MouseButtons.LEFT):
        self.d.xtest_fake_input(X.ButtonPress, button.value)
        self.d.sync()

    def mouse_release(self, button: int = 1):
        """
        Simulates releasing a previously pressed mouse button.
        """
        self.d.xtest_fake_input(X.ButtonRelease, button)
        self.d.sync()

    def mouse_release(self, button: MouseButtons = MouseButtons.LEFT):
        self.d.xtest_fake_input(X.ButtonRelease, button.value)
        self.d.sync()

    def get_screen_resolution(self):
        """
        Returns the screen resolution as a tuple (width, height).
        """
        return self.s.width_in_pixels, self.s.height_in_pixels
