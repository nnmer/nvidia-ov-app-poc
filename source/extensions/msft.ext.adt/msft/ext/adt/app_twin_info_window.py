__all__ = ["MsftAdtWindow"]
import os, time, copy
import omni.kit
import omni.ext
import omni.usd
import omni.ui as ui
import asyncio
from typing import List
from .style import *
from .adt import *
from .adt_list import *
from .adt_utils import AdtUtils
from .messenger import *
from .robotmotion import RobotMotion
from .mesh_materials import MeshMaterials
# from pxr import Sdf, Usd
# from .robotdata import getPose, RobotPose
from .viewport_utils import ViewportUtils
import omni.usd as usd
from .settings import Settings

class TreeListItem(ui.AbstractItem):
    """Single item of the model"""

    def __init__(self, text, parent_path = []):
        super().__init__()
        self.name_model = ui.SimpleStringModel(text)
        self.children = None
        self.parent_path = parent_path

class TreeListModel(ui.AbstractItemModel):
    def __init__(self, dataSource, *twins_ids):
        super().__init__()
        self._children = [TreeListItem(t) for t in twins_ids]
        self._data = dataSource

    def find(self, keys, json = None):
        if json == None:
            json = self._data

        rv = json
        for key in keys:
            rv = rv[key]
        return rv

    def get_item_children(self, item):
        """Returns all the children when the widget asks it."""
        if item is not None:
            if not item.children:
                cur_parent_path = (item.parent_path.copy())
                cur_parent_path.append(item.name_model.as_string)
                child_data_slice = self.find(cur_parent_path)
                if isinstance(child_data_slice, dict):
                    item.children = [TreeListItem(f"{i}", cur_parent_path) for i in child_data_slice.keys()]
            return item.children

        return self._children

    def get_item_value_model_count(self, item):
        """The number of columns"""
        return 2


    def get_item_value_model(self, item, column_id):
        """
        Return value model.
        It's the object that tracks the specific value.
        In our case we use ui.SimpleStringModel.
        """
        if column_id == 1:
            cur_parent_path = item.parent_path.copy()
            cur_parent_path.append(item.name_model.as_string)
            child_data_slice = self.find(cur_parent_path)
            x = ui.SimpleStringModel()
            if child_data_slice != None and type(child_data_slice) is not dict:
                x.set_value(child_data_slice)
            return x
        return item.name_model


class AppTwinInfoWindow(ui.Window):
    title = "Twin"

    _on_stage_selection_changed_event_handler = None
    _twins_to_list = {}
    _tree = None

    def __init__(self, **kwargs):
        super().__init__(AppTwinInfoWindow.title, ui.DockPreference.LEFT)
        # self.deferred_dock_in("Viewport", ui.DockPolicy.TARGET_WINDOW_IS_ACTIVE)
        # self.dock_in(ui.Workspace.get_window("Viewport"), ui.DockPosition.LEFT, 0.2)

        self._on_stage_selection_changed_event_handler = usd.get_context()\
            .get_stage_event_stream()\
            .create_subscription_to_pop(self._on_stage_selection_changed, name="msft.ext.adt onSelectionChanged")
        self.render_window_frame()

    def _on_stage_selection_changed(self, event):
        if event.type == int(usd.StageEventType.SELECTION_CHANGED) and Settings.get(Settings.UI_SHOW_TWIN_RAW_DATA_AT_APP_PANEL):
            paths = usd.get_context().get_selection().get_selected_prim_paths()
            self._twins_to_list = {}
            for prim_path in paths:
                dtId = AdtUtils.find_dt_id_by_prim_from_map(prim_path)
                query_expression = f"SELECT * FROM digitaltwins dt WHERE dt.$dtId = '{dtId}'"
                query_result = ADT().service_client().query_twins(query_expression)
                for i in query_result:
                    if bool(os.environ['OV_DEBUG']):
                        carb.log_warn(f"[{prim_path}] pulled DigitalTwin data => {i}")
                    # self.label_nyokkey_status = val +'-'+str(id(i))[-7:] if bool(os.environ["OV_DEV"]) == True else val
                    self._twins_to_list[prim_path] = dict(i)
            self.render_window_frame()
            if self._tree:
                for i in self._model.get_item_children(None):
                    self._tree.set_expanded(i, True, True)

    def render_window_frame(self):
        twins_keys = self._twins_to_list.keys()

        with self.frame:
            ui.Spacer(height=20)
            with ui.ScrollingFrame(
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                style_type_name_override="TreeView",
            ):
                self._model = TreeListModel(self._twins_to_list, *twins_keys)
                self._tree = ui.TreeView(self._model, root_visible=False, style={"margin": 0.5})



    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False
