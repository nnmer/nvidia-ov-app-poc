import carb

class KeyDown:
    def __init__(self):
        self.__input = carb.input.acquire_input_interface()

    def test(self, key_a, key_b):
        if self.__input.get_keyboard_button_flags(None, key_a) & carb.input.BUTTON_FLAG_DOWN:
            return True
        if self.__input.get_keyboard_button_flags(None, key_b) & carb.input.BUTTON_FLAG_DOWN:
            return True
        return False
