from msft.ext.viewport_widgets_manager import InfoWidgetProvider

class ViewportWidgetTwinInfo(InfoWidgetProvider):
    _whitelisted_props = (
        'ID',
        'Tags',
        'RobotStatus',
        'Temperature',
        'ang1j',
        'ang2j',
        'ang3j',
        'ang4j',
        'ang5j',
        'ang6j',
    )
