from Xlib import X, XK
from Xlib.ext import randr, xfixes
from enum import Enum
import time
from Xlib.xobject.cursor import Cursor
from typing import List, Dict, Tuple, Any

class Action(Enum):
    WAIT = 0
    KEY_STROKE = 1
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
    def __init__(self, display):
        self.d = display
        self.s = self.d.screen()
        self.root = self.s.root
        self.macros: Dict[str, List[Tuple[Action, Any]]] = {}



    def get_screen_resolution(self):
        """
        Returns the screen resolution as a tuple (width, height).
        """
        return self.s.width_in_pixels, self.s.height_in_pixels

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

    def execute_action(self, action: Action, *args):
        if action == Action.WAIT:
            time.sleep(args[0])
        elif action == Action.KEY_STROKE:
            self.key_stroke(args[0])
        elif action == Action.KEY_PRESS:
            self.key_press(args[0])
        elif action == Action.KEY_RELEASE:
            self.key_release(args[0])
        elif action == Action.KEY_SHORTCUT:
            self.shortcut(args[0])
        elif action == Action.MOUSE_MOVE:
            self.mouse_move(args[0], args[1])
        elif action == Action.MOUSE_CLICK:
            self.mouse_click(args[0])
        elif action == Action.MOUSE_PRESS:
            self.mouse_press(args[0])
        elif action == Action.MOUSE_RELEASE:
            self.mouse_release(args[0])
        else:
            raise Exception("Invalid action type.")
        
    def execute_actions(self, actions: list):
        for action in actions:
            self.execute_action(*action)

    def set_gamma(self, r: float, g: float, b: float):
        """
        Sets the gamma correction for the screen.
        :param r: Red gamma value (float)
        :param g: Green gamma value (float)
        :param b: Blue gamma value (float)
        """
        # Get the default screen and root window
        screen = self.s
        root = self.root

        # Get the resources (screen configuration)
        resources = randr.get_screen_resources(root)
        crtcs = resources.crtcs

        # Set gamma for each CRTC (display controller)
        for crtc in crtcs:
            gamma_size = randr.get_crtc_gamma_size(self.d, crtc).size
            red_gamma = [int((i / (gamma_size - 1)) ** r * 65535) for i in range(gamma_size)]
            green_gamma = [int((i / (gamma_size - 1)) ** g * 65535) for i in range(gamma_size)]
            blue_gamma = [int((i / (gamma_size - 1)) ** b * 65535) for i in range(gamma_size)]
            randr.set_crtc_gamma(self.d, crtc, gamma_size, red_gamma, green_gamma, blue_gamma)

        # Sync the display to apply changes
        self.d.sync()



    def add_macro(self, name: str, actions: list):
        self.macros[name] = actions

    def run_macro(self, name: str):
        self.execute_actions(self.macros[name])

    def remove_macro(self, name: str):
        del self.macros[name]
    
    def clear_macros(self):
        self.macros.clear()
    
    def get_macros(self):
        return self.macros
    
    def register_macro(self, name: str):
        self.add_macro(name, [])

    def add_action_to_macro(self, name: str, action: Action, *args):
        self.macros[name].append((action, *args))

    def remove_action_from_macro(self, name: str, index: int):
        del self.macros[name][index]

    def clear_macro(self, name: str):
        self.macros[name].clear()

    def __del__(self):
        self.set_gamma(1, 1, 1)
        self.d.close()


