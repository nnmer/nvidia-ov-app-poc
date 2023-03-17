import uuid
import omni.kit.app
import omni.ui as ui
import carb.events
from omni.kit.viewport_widgets_manager.widget_provider import WidgetProvider as WP
from typing import Callable

class WidgetProvider(WP):

    on_close_event_id = carb.events.type_from_string("msft.ext.viewport-widgets-provider.event.close_widget")
    bus = None

    def __init__(self, data = None, ) -> None:
        super().__init__()
        self._id = uuid.uuid4()

        self._data = data

    def get_id(self):
        return self._id

    def close(self):
        data={'ref': str(self._id)}
        omni.kit.app.get_app().get_message_bus_event_stream().push(event_type=WidgetProvider.on_close_event_id, payload=data)

    def get_data(self):
        return self._data

    def widget_header(self, render_widget_body_callback_fn: Callable, style={}):
        with ui.ZStack(height=10,width=200):
            ui.Rectangle(style=style)
            with ui.VStack(height=0, style={"margin":5}):
                with ui.HStack( style={"margin":0}, direction=ui.Direction.RIGHT_TO_LEFT):
                    ui.Button(text=' x ', width=0, height=0, clicked_fn=lambda *args: self.close()  )
                render_widget_body_callback_fn()

    def build_widget(self, viewport_window):
        # can call widget_header() to have a common header with closing button
        raise NotImplementedError("This function needs to be implemented.")