import os
import omni.ext
import omni.kit.ui
import omni.ui as ui
import omni.usd as usd
import carb
from  carb.events._events import IEvent

from .window import MsftKhiAnimationWindow
from msft.ext.adt import MsftAdtWindow, ADT, AdtUtils, AdtPullingRegistry, Messenger, MeshMaterials, ViewportWidgetTwinInfo, Settings
from msft.ext.adt.constants import Constants
from msft.ext.adt.mesh_materials import MaterialType, Constants
import msft.ext.viewport_widgets_manager as ViewportWidgetsManager
from msft.ext.viewport_widgets_manager import WidgetAlignment, AlertWidgetProvider, WidgetProvider, WIDGET_NO_CLOSE
from .viewport_widgets_store import ViewportWidgetsStore
from .widget_twins_list import TwinsListWidget
from pxr import Usd, UsdShade


class WindowExtension(omni.ext.IExt):

    MENU_PATH = "Window/MSFT KHI Animation"
    _on_stage_selection_changed_event_handler = None

    def on_startup(self, ext_id):

        editor_menu = omni.kit.ui.get_editor_menu()

        # Most application have an Window Menu, See MenuLayout to re-organize it
        self._window = None
        self._menu = editor_menu.add_item(WindowExtension.MENU_PATH, self._on_menu_click, toggle=True, value=True)
        self.show_window(True)

        self._alert_per_prim_map = {} # primId => tuple (widget uuid, widget wrapper weak reference)

        self.adtTwinMsgSubscriberHandler = Messenger().subscribe_deffered(Messenger().EVENT_ADT_MSG, self.process_twin_msg)
        self.robotSignalRMsgSubscriberHandler = Messenger().subscribe_deffered(Messenger().EVENT_SIGNALR_MSG, self.process_signalr_msg)
        self._stage_events_subscriber =  usd.get_context().get_stage_event_stream().create_subscription_to_pop(self._on_stage_opened_reset_mesh_instances)
        self._on_highlighted_prim_changed_subscriber = Messenger().subscribe_deffered(Messenger().EVENT_HIGHTLIGHTED_PRIMS_CHANGED, self._on_highlighted_prim_changed)

    #     self._subscr_on_close_event = omni.kit.app.get_app().get_message_bus_event_stream().create_subscription_to_pop_by_type(WidgetProvider.on_close_event_id, self.clear_alert_widget_reference)
        self._on_stage_selection_changed_event_handler = usd.get_context().get_stage_event_stream().create_subscription_to_pop(
            self._on_stage_selection_changed, name="msft.ext.adt onSelectionChanged"
        )

        AdtPullingRegistry().register_action('register_adt_twins_pull_action', TwinsListWidget()._register_adt_twins_pull_action)
        AdtPullingRegistry().start_action('register_adt_twins_pull_action')

    def _on_stage_selection_changed(self, event):
        if event.type == int(usd.StageEventType.SELECTION_CHANGED) and Settings.get(Settings.UI_SHOW_TWIN_VIEWPORT_POPUP_WHEN_SELECTED):
            paths = usd.get_context().get_selection().get_selected_prim_paths()

            set(ViewportWidgetsStore().keys()).symmetric_difference(paths)
            removed = list(set(ViewportWidgetsStore().keys()) - set(paths))
            added = list(set(paths) - set(ViewportWidgetsStore().keys()))

            for to_remove_prim in removed:
                try:
                    widget = ViewportWidgetsStore().pop(to_remove_prim)
                    ViewportWidgetsManager.remove_widget(widget)
                except:
                    pass

            for to_add_prim in added:
                key = AdtUtils.find_dt_id_by_prim_from_map(to_add_prim)
                if key != None:
                    twin_data = TwinsListWidget().twins.get(key)
                    infoWidget = ViewportWidgetTwinInfo(twin_data)
                    widget_id = ViewportWidgetsManager.add_widget(to_add_prim, infoWidget, WidgetAlignment.CENTER)
                    ViewportWidgetsStore().set(to_add_prim, widget_id)

    def _on_highlighted_prim_changed(self, event: IEvent):
        old_selections = list(event.payload['old']) if len(event.payload['old']) > 0 else ()
        new_selections = list(event.payload['new']) if len(event.payload['new']) > 0 else ()
        removed = list(set(old_selections) - set(new_selections))
        added = list(set(new_selections) - set(old_selections))
        stage = usd.get_context().get_stage()

        for item in removed:
            target_to_patch = AdtUtils.find_dt_id_by_prim_from_map(item)
            prim = stage.GetPrimAtPath(str(item))
            if str(prim) != Constants.INVALID_NULL_PRIM :
                name = prim.GetParent().GetName()

                if target_to_patch != None and name.startswith('RS007_'):
                    index = name.rfind('_')
                    selectedMesh = name[:index]+'.'+name[index+1:]
                    ADT().dt_update_property(target_to_patch, '/SelectedMesh', '')

        for item in added:
            target_to_patch = AdtUtils.find_dt_id_by_prim_from_map(item)
            prim = stage.GetPrimAtPath(str(item))
            if str(prim) != Constants.INVALID_NULL_PRIM :
                name = prim.GetParent().GetName()

                if target_to_patch != None and name.startswith('RS007_'):
                    index = name.rfind('_')
                    selectedMesh = name[:index]+'.'+name[index+1:]
                    ADT().dt_update_property(target_to_patch, '/SelectedMesh', selectedMesh)

    # def clear_alert_widget_reference(self, event):
    #     for prim_key in self._alert_per_prim_map.keys():
    #         if str(self._alert_per_prim_map[prim_key][0]) ==  event.payload['ref']:
    #             del self._alert_per_prim_map[prim_key]
    #             break

    def _on_stage_opened_reset_mesh_instances(self, e, prim_paths = (
            '/World',
            )):
        """
            Ensure all meshes on stage are not instances
            This may be not a very efficient way (to go through all the meshes) but works for current KHI use case.
            Optionally need to specify specific prim paths to iterate
        """
        if e.type == int(usd.StageEventType.OPENED):
            context = usd.get_context()
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
            root_prim_path = AdtUtils._map_dt_id2mesh_id.get(dtId)
            stage = usd.get_context().get_stage()
            if root_prim_path != None and stage:
                root_prim = stage.GetPrimAtPath(str(root_prim_path))

                range = Usd.PrimRange(root_prim)
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
                    if self._alert_per_prim_map.get(root_prim_path) == None:
                        alertWidget = AlertWidgetProvider([event.payload['LastErrorMessage']], config=[WIDGET_NO_CLOSE])
                        widget_id = ViewportWidgetsManager.add_widget(root_prim_path, alertWidget, WidgetAlignment.TOP)
                        self._alert_per_prim_map[root_prim_path] = (alertWidget.get_id(), widget_id)

                        material_prim = UsdShade.MaterialBindingAPI(root_prim).GetDirectBinding().GetMaterial().GetPrim()
                        if str(material_prim) == Constants.INVALID_NULL_PRIM:
                            MeshMaterials().highlight_prim(root_prim_path, MaterialType.MATERIAL_ERROR)
                else:
                    alert_set = self._alert_per_prim_map.get(root_prim_path)
                    if alert_set:
                        ViewportWidgetsManager.remove_widget(alert_set[1])
                        del self._alert_per_prim_map[root_prim_path]
                        material_prim = UsdShade.MaterialBindingAPI(root_prim).GetDirectBinding().GetMaterial().GetPrim()
                        print(f"remove error: str(material_prim): {str(material_prim)}, material_prim.GetPath(): {material_prim.GetPath()}")
                        if str(material_prim) != Constants.INVALID_NULL_PRIM \
                            and material_prim.GetPath() == MaterialType.MATERIAL_ERROR:

                            MeshMaterials().clear_prim_highlight(root_prim_path)



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
        AdtPullingRegistry().deregister_all_actions()
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