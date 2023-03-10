from omni.kit.viewport_widgets_manager.widget_provider import WidgetProvider as WP
import typing

class WidgetProvider(WP):
    def __init__(self, data = None) -> None:
        super().__init__()
        self._data = data
        self._on_close = None

    def set_action(self, on_close = typing.Callable[[], None]):
        self._on_close = on_close

    def get_data(self):
        return self._data

    def build_widget(self, window):
        raise NotImplementedError("This function needs to be implemented.")