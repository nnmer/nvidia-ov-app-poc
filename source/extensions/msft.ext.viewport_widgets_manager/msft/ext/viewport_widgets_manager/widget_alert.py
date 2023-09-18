import omni.ui as ui
from omni.ui import color as cl
from .widget_provider import WidgetProvider


class AlertWidgetProvider(WidgetProvider):
    def _render_body(self):
        with ui.VStack(width=300):
            ui.Label(str(self._data), name="text", word_wrap=True)

    def build_widget(self, viewport_window, style={
                    # "background_color": cl(0.2),
                    "background_color": cl("#700000bf"), #111eff   #00089f
                    "border_color": cl("#930000"),
                    "border_width": 1,
                    "border_radius": 4,
                }):
        with ui.ZStack(height=10, width=300, style={"margin":2}):
            ui.Rectangle(style=style)
            with ui.VStack(height=50):
                self.widget_header()
                self._render_body()