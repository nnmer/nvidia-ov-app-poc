from omni.kit.viewport.utility import get_active_viewport_window
import omni.ui as ui
from omni.ui import scene as sc
from omni.ui import color as cl
from pxr import Gf
from pxr import UsdGeom
from pxr import Usd
from pxr import UsdShade
from pxr import Tf
from pxr import UsdLux

import omni.usd
import omni.kit.commands


class WidgetInfoModel(sc.AbstractManipulatorModel):
    """
    User part. The model tracks the position and info of the selected object.
    """

    class PositionItem(sc.AbstractManipulatorItem):
        """
        The Model Item represents the position. It doesn't contain anything
        because because we take the position directly from USD when requesting.
        """

        def __init__(self):
            super().__init__()
            self.value = [0, 0, 0]

    class ValueItem(sc.AbstractManipulatorItem):
        """The Model Item contains a single float value about some attibute"""

        def __init__(self, value=0):
            super().__init__()
            self.value = [value]

    def __init__(self):
        super().__init__()

        self.material_name = ""
        self.position = WidgetInfoModel.PositionItem()

        # The distance from the bounding box to the position the model returns
        self._offset = 0
        # Current selection
        self._prim = None
        self._current_path = ""
        self._stage_listener = None

        # Save the UsdContext name (we currently only work with single Context)
        self._usd_context_name = ''
        usd_context = self._get_context()

        # Track selection
        self._events = usd_context.get_stage_event_stream()
        self._stage_event_sub = self._events.create_subscription_to_pop(
            self._on_stage_event, name="Object Info Selection Update"
        )

    def _get_context(self) -> Usd.Stage:
        # Get the UsdContext we are attached to
        return omni.usd.get_context(self._usd_context_name)

    def _notice_changed(self, notice, stage):
        """Called by Tf.Notice"""
        for p in notice.GetChangedInfoOnlyPaths():
            if self._current_path in str(p.GetPrimPath()):
                self._item_changed(self.position)

    def get_item(self, identifier):
        if identifier == "position":
            return self.position
        if identifier == "name":
            return self._current_path
        if identifier == "material":
            return self.material_name

    def get_as_floats(self, item):
        if item == self.position:
            # Requesting position
            return self._get_position()

        if item:
            # Get the value directly from the item
            return item.value
        return []

    def set_floats(self, item, value):
        if not self._current_path:
            return

        if not value or not item or item.value == value:
            return

        # Set directly to the item
        item.value = value
        # This makes the manipulator updated
        self._item_changed(item)

    def _on_stage_event(self, event):
        """Called by stage_event_stream"""
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            self._on_kit_selection_changed()

    def _on_kit_selection_changed(self):
        # selection change, reset it for now
        self._current_path = ""
        usd_context = self._get_context()
        stage = usd_context.get_stage()
        if not stage:
            return

        prim_paths = usd_context.get_selection().get_selected_prim_paths()
        if not prim_paths:
            self._item_changed(self.position)
            # Revoke the Tf.Notice listener, we don't need to update anything
            if self._stage_listener:
                self._stage_listener.Revoke()
                self._stage_listener = None
            return

        prim = stage.GetPrimAtPath(prim_paths[0])

        if prim.IsA(UsdLux.Light):
            print("Light")
            self.material_name = "I am a Light"
        elif prim.IsA(UsdGeom.Imageable):
            material, relationship = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
            if material:
                self.material_name = str(material.GetPath())
            else:
                self.material_name = "N/A"
        else:
            self._prim = None
            return

        self._prim = prim
        self._current_path = prim_paths[0]

        # Add a Tf.Notice listener to update the position
        if not self._stage_listener:
            self._stage_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._notice_changed, stage)

        (old_scale, old_rotation_euler, old_rotation_order, old_translation) = omni.usd.get_local_transform_SRT(prim)

        # Position is changed
        self._item_changed(self.position)

    def _get_position(self):
        """Returns position of currently selected object"""
        stage = self._get_context().get_stage()
        if not stage or not self._current_path:
            return [0, 0, 0]

        # Get position directly from USD
        prim = stage.GetPrimAtPath(self._current_path)
        box_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), includedPurposes=[UsdGeom.Tokens.default_])
        bound = box_cache.ComputeWorldBound(prim)
        range = bound.ComputeAlignedBox()
        bboxMin = range.GetMin()
        bboxMax = range.GetMax()

        position = [(bboxMin[0] + bboxMax[0]) * 0.5, bboxMax[1] + self._offset, (bboxMin[2] + bboxMax[2]) * 0.5]
        return position

class WidgetInfoManipulator(sc.Manipulator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.destroy()

        self._radius = 2
        self._distance_to_top = 5
        self._thickness = 2
        self._radius_hovered = 20
        self._prims_path_allowed_select_show = kwargs.get('prims_path_allowed_select_show')

    def destroy(self):
        self._root = None
        # self._slider_subscription = None
        # self._slider_model = None
        self._name_label = None

    def _on_build_widgets(self):
        with ui.ZStack():
            ui.Rectangle(
                style={
                    # "background_color": cl(0.2),
                    "background_color": cl("#ff2828bd"),
                    "border_color": cl(1),
                    "border_width": 2,
                    "border_radius": 4,
                }
            )
            with ui.VStack(style={"font_size": 24}):
                ui.Spacer(height=4)
                with ui.ZStack(style={"margin": 1}, height=30):
                    ui.Rectangle(
                        style={
                            "background_color": cl(0.0),
                        }
                    )
                    ui.Line(style={"color": cl(0.7), "border_width": 2}, alignment=ui.Alignment.BOTTOM)
                    # ui.Label("Hello world, I am a scene.Widget!", height=0, alignment=ui.Alignment.CENTER)

                ui.Spacer(height=4)
                self._name_label = ui.Label("", height=0, alignment=ui.Alignment.CENTER, word_wrap=True, style={'font_size': 24})

                # setup some model, just for simple demonstration here
                # self._slider_model = ui.SimpleFloatModel()

                # ui.Spacer(height=10)
                # with ui.HStack():
                #     ui.Spacer(width=10)
                #     ui.Label("scale", height=0, width=0)
                #     ui.Spacer(width=5)
                #     ui.FloatSlider(self._slider_model)
                #     ui.Spacer(width=10)
                # ui.Spacer(height=4)
                # ui.Spacer()

        self.on_model_updated(None)

        # Additional gesture that prevents Viewport Legacy selection
        # self._widget.gestures += [_DragGesture()]

    def on_build(self):
        """Called when the model is chenged and rebuilds the whole slider"""
        self._root = sc.Transform(visible=False)
        with self._root:
            with sc.Transform(scale_to=sc.Space.SCREEN):
                with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 100, 0)):
                    # Label
                    with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                        self._widget = sc.Widget(500, 150, update_policy=sc.Widget.UpdatePolicy.ON_MOUSE_HOVERED)
                        self._widget.frame.set_build_fn(self._on_build_widgets)

    def on_model_updated(self, _):
        # if we don't have selection then show nothing
        if not self.model or not self.model.get_item("name"):
            self._root.visible = False
            return

        managed_path = False
        for key in self._prims_path_allowed_select_show:
            if self.model.get_item('name').startswith(key):
                managed_path = True
                break

        if not managed_path:
            self._root.visible = False
            return

        print(f"Selected model {self.model.get_item('name')}")
        print(self._prims_path_allowed_select_show)

        # Update the shapes
        position = self.model.get_as_floats(self.model.get_item("position"))
        self._root.transform = sc.Matrix44.get_translation_matrix(*position)
        self._root.visible = True

        # Update the slider
        def update_scale(prim_name, value):
            print(f"changing scale of {prim_name}, {value}")

        # if self._slider_model:
        #     self._slider_subscription = None
        #     self._slider_model.as_float = 1.0
        #     self._slider_subscription = self._slider_model.subscribe_value_changed_fn(
        #         lambda m, p=self.model.get_item("name"): update_scale(p, m.as_float)
        #     )

        # Update the shape name
        if self._name_label:
            self._name_label.text = f"Prim:{self.model.get_item('name')}"



# class AlertViewportWidget(vwm.WidgetProvider):
class AlertViewportWidget():
    """The Object Info Manupulator, placed into a Viewport"""

    def __init__(self, viewport_window, ext_id: str, prims_path_allowed_select_show: dict):
        """
            prims_path_allowed_select_show - a dictionary of keys to allow alert to be used
                selected prim will be compared  to startwith(a key from dictionary)
        """
        self._scene_view = None
        self._viewport_window = viewport_window

        # Create a unique frame for our SceneView
        with self._viewport_window.get_frame(ext_id):
            # Create a default SceneView (it has a default camera-model)
            self._scene_view = sc.SceneView()
            # Add the manipulator into the SceneView's scene
            with self._scene_view.scene:
                WidgetInfoManipulator(model=WidgetInfoModel(), prims_path_allowed_select_show=prims_path_allowed_select_show)

            # Register the SceneView with the Viewport to get projection and view updates
            self._viewport_window.viewport_api.add_scene_view(self._scene_view)

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self._scene_view:
            # Empty the SceneView of any elements it may have
            self._scene_view.scene.clear()
            # Be a good citizen, and un-register the SceneView from Viewport updates
            if self._viewport_window:
                self._viewport_window.viewport_api.remove_scene_view(self._scene_view)
        # Remove our references to these objects
        self._viewport_window = None
        self._scene_view = None
