import uuid
import omni.kit.app
import carb.events
from omni.kit.viewport_widgets_manager.widget_provider import WidgetProvider as WP


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

    def build_widget(self, window):
        raise NotImplementedError("This function needs to be implemented.")