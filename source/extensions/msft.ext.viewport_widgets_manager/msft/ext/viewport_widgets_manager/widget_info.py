import omni.ui as ui
from omni.ui import color as cl
from .widget_provider import WidgetProvider

class InfoWidgetProvider(WidgetProvider):
    """
        Info widget, showing a list of properties in a kkey value structure
    """

    _whitelisted_props = (
        'ID',
        'Tags',
        'RobotStatus',
        'Temperature'
    )

    def _order_and_filter_data(self):
        records = dict.copy(self._data)
        if self._whitelisted_props:
            records = dict((k, v) for k, v in records.items() if k in self._whitelisted_props)
        result = dict(sorted(records.items(), key=lambda kv: kv[0]))
        return result

    def build_widget(self, viewport_window):
        with ui.ZStack(height=10,width=200):
            ui.Rectangle(
                style={
                    # "background_color": cl(0.2),
                    "background_color": cl("#000670bf"), #111eff   #00089f
                    "border_color": cl("#00055c"),
                    "border_width": 1,
                    "border_radius": 4,
                }
            )

            with ui.VStack(height=0, style={"margin":5}):
                with ui.HStack( style={"margin":0}, direction=ui.Direction.RIGHT_TO_LEFT):
                    ui.Button(text=' x ', width=0, height=0, clicked_fn=lambda *args: self.close()  )
                for key in self._order_and_filter_data():
                    with ui.HStack(width=0,style={"margin":0}):
                        ui.Label(key, name="prop_label", word_wrap=True,width=100)
                        ui.Label(str(self._data[key]), name="prop_value")
