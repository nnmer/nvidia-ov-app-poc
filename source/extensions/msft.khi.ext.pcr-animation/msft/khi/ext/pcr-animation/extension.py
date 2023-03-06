import os
import omni.ext
import omni.kit.ui

from .window import MsftKhiAnimationWindow
from msft.ext.adt.messenger import Messenger


class WindowExtension(omni.ext.IExt):

    MENU_PATH = "Window/MSFT KHI Animation"

    def on_startup(self, ext_id):

        editor_menu = omni.kit.ui.get_editor_menu()

        # Most application have an Window Menu, See MenuLayout to re-organize it
        self._window = None
        self._menu = editor_menu.add_item(WindowExtension.MENU_PATH, self._on_menu_click, toggle=True, value=True)
        self.show_window(True)

        self.adtTwinMsgSubscriberHandler = Messenger().subscribe_deffered(Messenger().EVENT_ADT_MSG, self.process_twin_msg)
        self.robotSignalRMsgSubscriberHandler = Messenger().subscribe_deffered(Messenger().EVENT_SIGNALR_MSG, self.process_signalr_msg)


    def process_twin_msg(self,event):
        if bool(os.environ['OV_DEBUG']):
            print('EVENT_ADT_MSG is here do something with it')
            print(str(event.type))
            print(str(event.payload))

        import datetime
        self._window.label_msg_adt.text = f"{datetime.datetime.now().time()}::{str(event.payload['$dtId'])}::{str(event.payload['$metadata']['$lastUpdateTime'])}"
        event.consume()

    def process_signalr_msg(self,event):
        if bool(os.environ['OV_DEBUG']):
            print('EVENT_SIGNALR_MSG is here do something with it')
            print(str(event.type))
            print(str(event.payload))

        self._window.label_msg_signalr.text = str(event.payload)
        event.consume()



    def _on_menu_click(self, menu, toggled):
        self.show_window(toggled)

    def show_window(self, toggled):
        if toggled:
            if self._window is None:
                self._window = MsftKhiAnimationWindow()
                self._window.set_visibility_changed_fn(self._visiblity_changed_fn)
            else:
                self._window.show()
        else:
            if self._window is not None:
                self._window.hide()

    def _visiblity_changed_fn(self, visible):
        if self._menu:
            omni.kit.ui.get_editor_menu().set_value(WindowExtension.MENU_PATH, visible)
            self.show_window(visible)

    def on_shutdown(self):
        if self._window is not None:
            self._window.destroy()
            self._window = None
            self.adtTwinMsgSubscriberHandler = None
            self.robotSignalRMsgSubscriberHandler = None
        if self._menu is not None:
            editor_menu = omni.kit.ui.get_editor_menu()
            editor_menu.remove_item(self._menu)
            self._menu = None
