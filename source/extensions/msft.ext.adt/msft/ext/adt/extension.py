import omni.ext
import omni.kit.ui

from .window import MsftAdtWindow
from .socket_messaging_window import SocketMessagingWindow

class WindowExtension(omni.ext.IExt):

    MENU_PATH = "Window/Websockets ADT Requests"

    def on_startup(self, ext_id):

        editor_menu = omni.kit.ui.get_editor_menu()

        # Most application have an Window Menu, See MenuLayout to re-organize it
        self._window = None
        self._sockets_window = None
        self._menu = editor_menu.add_item(WindowExtension.MENU_PATH, self._on_menu_click, toggle=True, value=True)
        self.show_window(True)

    def _on_menu_click(self, menu, toggled):
        self.show_window(toggled)

    def show_window(self, toggled):
        if toggled:
            if self._window is None:
                self._window = MsftAdtWindow()
                self._window.set_visibility_changed_fn(self._visiblity_changed_fn)
                self._sockets_window = SocketMessagingWindow()
                self._sockets_window.set_visibility_changed_fn(self._visiblity_changed_fn)
            else:
                self._window.show()
                self._sockets_window.show()
        else:
            if self._window is not None:
                self._window.hide()
                self._sockets_window.hide()

    def _visiblity_changed_fn(self, visible):
        if self._menu:
            omni.kit.ui.get_editor_menu().set_value(WindowExtension.MENU_PATH, visible)
            self.show_window(visible)

    def on_shutdown(self):
        #omni.kit.commands.unsubscribe_on_change(self._event_triggered)
        print("[company.hello.world] MyExtension shutdown")

        if self._window is not None:
            self._window.destroy()
            self._window = None
            self._sockets_window.destroy()
            self._sockets_window = None
        if self._menu is not None:
            editor_menu = omni.kit.ui.get_editor_menu()
            editor_menu.remove_item(self._menu)
            self._menu = None
