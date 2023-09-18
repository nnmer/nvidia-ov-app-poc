import carb.settings

class Settings:
    UI_ZOOM_INOUT_ON_PRIM_SELECTION = "/exts/msft.ext.adt/zoom/inout_on_prim_selection"
    UI_ZOOM_IN_VALUE = "/exts/msft.ext.adt/zoom/in_value"
    UI_SHOW_TWIN_RAW_DATA_AT_APP_PANEL = "/exts/msft.ext.adt/show_twin_raw_data_at_app_panel"
    UI_SHOW_TWIN_VIEWPORT_POPUP_WHEN_SELECTED = "/exts/msft.ext.adt/show_twin_viewport_popup_wehen_selected"

    @staticmethod
    def get(key:str):
        settings = carb.settings.get_settings()
        return settings.get(key)

    @staticmethod
    def set(key:str, value):
        settings = carb.settings.get_settings()
        return settings.set(key, value)

    @staticmethod
    def set_default(key, value):
        settings = carb.settings.get_settings()
        return settings.set_default(key, value)

    @staticmethod
    def set_persistent(key, value):
        new_key = f"/persistent{key}"
        Settings.set(new_key, value)