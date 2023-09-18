import omni.ext
import omni.kit.ui
import omni.kit.app
import omni.ui as ui
import omni.usd as usd

from .viewport_utils import ViewportUtils
from .window import MsftAdtWindow
from .app_twin_info_window import AppTwinInfoWindow
from .mesh_materials import MeshMaterials
from .socket_messaging_window import SocketMessagingWindow
from .settings import Settings

class WindowExtension(omni.ext.IExt):

    MENU_PATH = "Window/Websockets ADT Requests"
    _on_stage_selection_changed_event_handler = None
    _settings_event_listeners = []
    _twin_data_window = None

    def on_startup(self, ext_id):

        editor_menu = omni.kit.ui.get_editor_menu()

        # Most application have an Window Menu, See MenuLayout to re-organize it
        self._window = None
        self._sockets_window = None
        self._menu = editor_menu.add_item(WindowExtension.MENU_PATH, self._on_menu_click, toggle=True, value=True)
        self.show_window(True)
        self._mesh_materials = MeshMaterials()
        self._mesh_materials.start()

        # setup extension default settings
        self._settings_event_listeners.append(
            omni.kit.app.SettingChangeSubscription(Settings.UI_SHOW_TWIN_RAW_DATA_AT_APP_PANEL, self._show_twin_data_window)
        )
        self._settings_event_listeners.append(
            omni.kit.app.SettingChangeSubscription(Settings.UI_ZOOM_IN_VALUE, self._rezoom_selected_prim)
        )

        self._on_stage_selection_changed_event_handler = usd.get_context().get_stage_event_stream().create_subscription_to_pop(
            self._on_stage_selection_changed, name="msft.ext.adt onSelectionChanged"
        )

    def _rezoom_selected_prim(self,tree_item=None,event_type=None):
        if Settings.get(Settings.UI_ZOOM_INOUT_ON_PRIM_SELECTION) == True:
            paths = usd.get_context().get_selection().get_selected_prim_paths()
            # carb.log_warn(paths)
            if (len(paths)==0):
                paths=['/World/group1']                 # FIXME: need to make this configurable
                ViewportUtils.focus_at_prim(paths, 0.15)  # FIXME: need to make this configurable
            else:
                ViewportUtils.focus_at_prim(paths, Settings.get(Settings.UI_ZOOM_IN_VALUE))

    def _on_stage_selection_changed(self, event):
        if event.type == int(usd.StageEventType.SELECTION_CHANGED):
            self._rezoom_selected_prim()

    def _show_twin_data_window(self, a, b):
        if Settings.get(Settings.UI_SHOW_TWIN_RAW_DATA_AT_APP_PANEL):
            if not self._twin_data_window:
                self._twin_data_window = AppTwinInfoWindow()
                self._twin_data_window.show()
                viewport = ui.Workspace.get_window("Viewport")
                if viewport:
                    self._twin_data_window.dock_in_window("Viewport", ui.DockPosition.LEFT, 0.4)
        else:
            if self._twin_data_window:
                self._twin_data_window.destroy()
                self._twin_data_window = None

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
        for i in self._settings_event_listeners:
            del i
        #omni.kit.commands.unsubscribe_on_change(self._event_triggered)

        if self._window is not None:
            self._window.destroy()
            self._window = None
            self._sockets_window.destroy()
            self._sockets_window = None
        if self._menu is not None:
            editor_menu = omni.kit.ui.get_editor_menu()
            editor_menu.remove_item(self._menu)
            self._menu = None
