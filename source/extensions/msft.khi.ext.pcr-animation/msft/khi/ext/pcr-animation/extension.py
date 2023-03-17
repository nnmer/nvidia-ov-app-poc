import os
import omni.ext
import omni.kit.ui
import omni.usd
import carb

from .window import MsftKhiAnimationWindow
from msft.ext.adt.messenger import Messenger
from msft.ext.adt.window import MsftAdtWindow
from msft.ext.adt.mesh_materials import MeshMaterials, MaterialType, Constants
import msft.ext.viewport_widgets_manager as ViewportWidgetsManager
from msft.ext.viewport_widgets_manager import WidgetAlignment, AlertWidgetProvider

from pxr import Usd, UsdShade


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
        self._stage_events_subscriber =  omni.usd.get_context().get_stage_event_stream().create_subscription_to_pop(self._on_stage_opened_reset_mesh_instances)

    def _on_stage_opened_reset_mesh_instances(self, e, prim_paths = (
            '/World',
            )):
        """
            Ensure all meshes on stage are not instances
            This may be not a very efficient way (to go through all the meshes) but works for current KHI use case.
            Optionally need to specify specific prim paths to iterate
        """
        if e.type == int(omni.usd.StageEventType.OPENED):
            context = omni.usd.get_context()
            stage = context.get_stage()
            for prim_path in list(prim_paths):
                if str(prim_path).startswith('/World'):
                    try:
                        prim = stage.GetPrimAtPath(str(prim_path))

                        if prim.IsInstance():
                            prim.SetInstanceable(False)

                        children_refs = prim.GetAllChildren()
                        if len(children_refs) > 0:
                            self._on_stage_opened_reset_mesh_instances(e, (x.GetPrimPath() for x in children_refs))
                    except:
                        carb.log_warn('Stage context is not ready yet. No /World')


    def process_twin_msg(self,event):
        dtId = str(event.payload['$dtId'])

        if dtId.startswith('RS07'):
            selected_prim = str(event.payload['SelectedMesh']).replace('.','_')
            has_error = bool(event.payload['UnitScenarioRobotStop'])
            root_prim_path = MsftAdtWindow._map_dt_id2mesh_id.get(dtId)
            if root_prim_path != None:
                stage = omni.usd.get_context().get_stage()
                prim = stage.GetPrimAtPath(str(root_prim_path))

                range = Usd.PrimRange(prim)
                for prim2 in range:
                    # print (f"Traversing prim: {prim2.GetPath()}")
                    if len(selected_prim)==0 or prim2.GetName() != selected_prim:
                        material_prim = UsdShade.MaterialBindingAPI(prim2).GetDirectBinding().GetMaterial().GetPrim()
                        if str(material_prim) != Constants.INVALID_NULL_PRIM \
                            and material_prim.GetPath() == MaterialType.MATERIAL_SELECTED:

                            MeshMaterials().clear_prim_highlight(prim2.GetPath())

                for prim2 in range:
                    if prim2.GetName() == selected_prim:
                        target = prim2.GetChildren()
                        if len(target)>0:
                            MeshMaterials().highlight_prim(target[0].GetPath())

                if has_error:
                    alertWidget = AlertWidgetProvider({dtId: {'twin_data': event.payload}, 'mesh_id': root_prim_path})
                    widget_id = ViewportWidgetsManager.add_widget(root_prim_path, alertWidget, WidgetAlignment.TOP)

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
            self._stage_events_subscriber = None
        if self._menu is not None:
            editor_menu = omni.kit.ui.get_editor_menu()
            editor_menu.remove_item(self._menu)
            self._menu = None
