import msft.ext.viewport_widgets_manager as ViewportWidgetsManager

class ViewportWidgetsStore:

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ViewportWidgetsStore, cls).__new__(cls)
            cls._viewport_widget_window_list = {}
        return cls.instance

    def get(self, key: str):
        return self._viewport_widget_window_list.get(key)

    def pop(self, key: str):
        return self._viewport_widget_window_list.pop(key)

    def set(self, key:str, value: any):
        self._viewport_widget_window_list[key] = value

    def keys(self):
        return self._viewport_widget_window_list.keys()

    def clean_all(self):        
        x = self.keys()
        for key in self.keys():
            widget = self.get(key)
            ViewportWidgetsManager.remove_widget(widget)
        self._viewport_widget_window_list = {}