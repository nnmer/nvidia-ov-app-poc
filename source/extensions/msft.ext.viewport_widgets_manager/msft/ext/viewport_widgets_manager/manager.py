from omni.kit.viewport_widgets_manager.manager import ViewportWidgetsManager as OmniViewportWidgetsManager, WidgetWrapper as OmniWidgetWrapper
from omni.kit.viewport_widgets_manager import WidgetAlignment as OmniWidgetAlignment
import omni.kit.app
import omni.ui as ui
import carb
import weakref
from carb.events import IEvent
from pxr import Sdf, UsdGeom, Trace
from .widget_provider import WidgetProvider
from omni.kit.viewport.utility import (
    get_active_viewport_window,
    get_ui_position_for_prim,
    ViewportPrimReferencePoint
)

class WidgetAlignment(OmniWidgetAlignment):
    pass

class WidgetWrapper(OmniWidgetWrapper):
    @Trace.TraceFunction
    def update_widget_position(self, cached_position=None):
        if not self._widget_provider.is_pinned:
            return super().update_widget_position(cached_position)
        else:
            return True
        
    def create_or_update_widget(self, cached_position=None):
        viewport_window = self._window or get_active_viewport_window()
        if (viewport_window is None) or (not viewport_window.visible):
            self.clear()
            return

        stage = viewport_window.viewport_api.stage
        if not stage:
            self.clear()
            return

        prim = stage.GetPrimAtPath(self.prim_path)
        if not prim:
            self.clear()
            return

        # If prim is hidden, clearing the widget.
        if (
            not self._is_prim_visible(stage, prim) or
            not self._is_camera_mesh_visible(stage, prim)
        ):
            self.clear()
            return

        if not self._viewport_placer:
            self._anchoring = True
            with self._canvas:
                self._viewport_placer = ui.Placer(draggable=True) # draggable=True is important
                with self._viewport_placer:
                    self._layout = ui.HStack(width=0, height=0)
                    with self._layout:
                        self._widget_provider.build_widget(viewport_window)

        if not self.update_widget_position(cached_position):
            self.clear()

class ViewportWidgetsManager(OmniViewportWidgetsManager):
    bus = None

    def __init__(self, usd_context_name=""):
        super().__init__(usd_context_name)
        self._provider_vs_wrapper_map = {}

    def _do_widget_close(self, event: IEvent):
        payload = event.payload
        if event.type == WidgetProvider.on_close_event_id:
            widget_id = self._provider_vs_wrapper_map.get(payload['ref'])
            if widget_id is not None:
                self.remove_widget(widget_id)

    def start(self):
        super().start()
        self.bus = omni.kit.app.get_app().get_message_bus_event_stream().create_subscription_to_pop_by_type(WidgetProvider().on_close_event_id, self._do_widget_close)

    def stop(self):
        super().stop()
        self.bus = None
          
    """
        Function is taked from the parent class, with one difference - we don't want to hide widgets when we do 
        camera manipulation. Commented out `self._hide_all_widgets()` in `for path in notice.GetChangedInfoOnlyPaths():`
        loop
    """          
    @Trace.TraceFunction
    def _on_objects_changed(self, notice, stage):        
        if stage != self._usd_context.get_stage():
            return

        for path in notice.GetResyncedPaths():
            if path == Sdf.Path.absoluteRootPath:
                self._pending_update_all = True
                self._current_wait_frames = 0
                # TRICK: Hides all widgets to delay the refresh
                # to avoid let user be aware of the delay.
                self._hide_all_widgets()
            else:
                self._pending_update_prim_paths.add(path)

        for path in notice.GetChangedInfoOnlyPaths():
            prim_path = path.GetPrimPath()
            # self._last_active_camera_path may be None, so make sure an
            # implicit Sdf.Path isn't constructed for equality comparison
            if (
                prim_path == Sdf.Path.absoluteRootPath or
                (
                    self._last_active_camera_path and
                    prim_path == self._last_active_camera_path
                )
            ):
                self._pending_update_all = True
                self._current_wait_frames = 0
                # self._hide_all_widgets()
            else:
                self._pending_update_prim_paths.add(prim_path)            

    def add_widget(self, prim_path: Sdf.Path, widget: WidgetProvider, alignment=WidgetAlignment.CENTER):
        usd_context = self._viewport_window.viewport_api.usd_context
        stage = usd_context.get_stage()
        usd_prim = stage.GetPrimAtPath(prim_path) if stage else False
        if usd_prim:
            xformable_prim = UsdGeom.Xformable(usd_prim)
        else:
            xformable_prim = None
        
        if not xformable_prim:
            carb.log_warn(f"Cannot add viewport widget for non-xformable prim.")
            return None
        # wrapperRef = super().add_widget(prim_path, widget, alignment)

        # next block taken from the parent class to overwrite WidgetWrapper
        carb.log_info(f"Adding prim widget for {prim_path}")
        widget_wrapper = WidgetWrapper(
            usd_context=self._usd_context, 
            prim_path=prim_path, 
            widget_provider=widget, 
            alignment=alignment,
            viewport_window=self._viewport_window, 
            viewport_canvas=self._frame_canvas,
            )
        self._all_widgets.append(widget_wrapper)
        if not self._last_active_camera_path or prim_path != self._last_active_camera_path:
            widget_wrapper.create_or_update_widget()

        wrapperRef = weakref.ref(widget_wrapper)
        #################################

        providerId = str(widget.get_id())
        self._provider_vs_wrapper_map[providerId] = wrapperRef

        return wrapperRef
