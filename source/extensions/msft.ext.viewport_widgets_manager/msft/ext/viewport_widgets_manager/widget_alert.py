import omni.ui as ui
from omni.ui import color as cl
from .widget_provider import WidgetProvider


class AlertWidgetProvider(WidgetProvider):
    def _render_body(self):
        with ui.VStack(style={"margin":0}, width=300):
            for item in self._data:
                ui.Label(str(item), name="text", word_wrap=True)

    def build_widget(self, viewport_window, style={
                    # "background_color": cl(0.2),
                    "background_color": cl("#700000bf"), #111eff   #00089f
                    "border_color": cl("#930000"),
                    "border_width": 1,
                    "border_radius": 4,
                }):

        self.widget_header(style=style, render_widget_body_callback_fn=self._render_body)