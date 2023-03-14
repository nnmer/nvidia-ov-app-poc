import omni.ui as ui
from omni.ui import color as cl
from .widget_provider import WidgetProvider


class AlertWidgetProvider(WidgetProvider):
    def build_widget(self, viewport_window):

        with ui.ZStack(height=10,width=200):
            ui.Rectangle(
                style={
                    # "background_color": cl(0.2),
                    "background_color": cl("#700000bf"), #111eff   #00089f
                    "border_color": cl("#930000"),
                    "border_width": 1,
                    "border_radius": 4,
                }
            )
            with ui.VStack(height=0, style={"margin":5}):
                with ui.HStack( style={"margin":0}, direction=ui.Direction.RIGHT_TO_LEFT):
                    ui.Button(text=' x ', width=0, height=0, clicked_fn=lambda *args: self.close()  )

                with ui.VStack(style={"margin":0}):
                    ui.Label("Error!!!", name="text", word_wrap=True)
                    ui.Label('Break break break stop stop stop', name="text", word_wrap=True)
