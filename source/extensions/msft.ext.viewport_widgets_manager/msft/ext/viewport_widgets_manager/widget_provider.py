import uuid
import omni.kit.app
import omni.ui as ui
import carb.events
from omni.kit.viewport_widgets_manager.widget_provider import WidgetProvider as WP
from typing import Callable

__all__ = [
    "WidgetProvider",
    "WIDGET_NO_CLOSE"
]

WIDGET_NO_CLOSE = 1000

class WidgetProvider(WP):

    is_pinned = False
    on_close_event_id = carb.events.type_from_string("msft.ext.viewport-widgets-provider.event.close_widget")
    bus = None
    _ui_header_frame = None

    def __init__(self, data=None, config=[]) -> None:
        super().__init__()
        self._id = uuid.uuid4()
        self._config = config

        self._data = data

    def get_id(self):
        return self._id

    def close(self):
        data = {"ref": str(self._id)}
        omni.kit.app.get_app().get_message_bus_event_stream().push(
            event_type=WidgetProvider.on_close_event_id, payload=data
        )
    
    def togglePin(self):
        self.is_pinned = not self.is_pinned
        self._widget_header()

    def get_data(self):
        return self._data

    def _widget_header(self):
        with self._ui_header_frame:
            with ui.Stack(ui.Direction.RIGHT_TO_LEFT):
                if WIDGET_NO_CLOSE not in self._config:
                    ui.Button(text=" x ", width=0, height=0, clicked_fn=lambda *args: self.close())
                ui.Button(text="Unpin" if self.is_pinned else "Pin", width=0, height=0, clicked_fn=lambda *args: self.togglePin())
                ui.Spacer()

    def widget_header(self, style={"margin":2}):
        with ui.VStack(height=0,style=style):        
            self._ui_header_frame = ui.Frame(name="ui_widget_header_frame")
            self._widget_header()

    def build_widget(self, viewport_window):
        # can call widget_header() to have a common header with closing button
        raise NotImplementedError("This function needs to be implemented.")
