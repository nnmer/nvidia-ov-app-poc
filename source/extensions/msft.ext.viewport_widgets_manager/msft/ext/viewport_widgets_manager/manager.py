from omni.kit.viewport_widgets_manager.manager import ViewportWidgetsManager as OmniViewportWidgetsManager
from omni.kit.viewport_widgets_manager import WidgetAlignment as OmniWidgetAlignment
import omni.kit.app
from pxr import Sdf
from .widget_provider import WidgetProvider

class WidgetAlignment(OmniWidgetAlignment):
    pass

class ViewportWidgetsManager(OmniViewportWidgetsManager):
    bus = None

    def __init__(self, usd_context_name=""):
        super().__init__(usd_context_name)
        self._provider_vs_wrapper_map = {}

    def _do_widget_close(self, event):
        payload = event.payload
        if event.type == WidgetProvider.on_close_event_id:
            widget_id = self._provider_vs_wrapper_map.get(payload['ref'])
            if widget_id is not None:
                self.remove_widget(widget_id)

    def start(self):
        super().start()
        self.bus = omni.kit.app.get_app().get_message_bus_event_stream().create_subscription_to_pop_by_type(WidgetProvider().on_close_event_id, self._do_widget_close)

    def stop(self):
        super().stop()
        self.bus = None

    def add_widget(self, prim_path: Sdf.Path, widget: WidgetProvider, alignment=WidgetAlignment.CENTER):
        wrapperRef = super().add_widget(prim_path, widget, alignment)
        providerId = str(widget.get_id())
        self._provider_vs_wrapper_map[providerId] = wrapperRef

        return wrapperRef
