import omni.usd
import carb
from .gesture import KeyDown
from .constants import Constants
from .messenger import Messenger
from pxr import Usd, Sdf, UsdShade



class MaterialType():
    MATERIAL_ERROR = '/World/Looks/ErrorOverlayMaterial'
    MATERIAL_SELECTED = '/World/Looks/SelectedOverlayMaterial'

class MeshMaterials():
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MeshMaterials, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self._hightlighted_prims = []

    def start(self):
        # Track selection
        usd_context = self._get_context()
        self._events = usd_context.get_stage_event_stream()
        self._stage_event_sub = self._events.create_subscription_to_pop(
            self._on_stage_event, name="Object Info Selection Update"
        )

    def _get_context(self) -> Usd.Stage:
        # Get the UsdContext we are attached to
        return omni.usd.get_context()

    def _on_stage_event(self, event):
        """Called by stage_event_stream"""
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            self._on_kit_selection_changed()

    def _on_kit_selection_changed(self):
        alt_down = KeyDown().test(carb.input.KeyboardInput.LEFT_ALT, carb.input.KeyboardInput.RIGHT_ALT)
        old_hightlighted_prims = self._hightlighted_prims.copy()
        if alt_down:
            context = self._get_context()
            stage = context.get_stage()

            prim_paths = self._get_context().get_selection().get_selected_prim_paths()
            for prim_path in prim_paths:
                carb.log_info(f"adt selected prim {prim_path}")

                prim = stage.GetPrimAtPath(prim_path)

                material_prim = UsdShade.MaterialBindingAPI(prim).GetDirectBinding().GetMaterial().GetPrim()
                if str(material_prim) != Constants.INVALID_NULL_PRIM \
                    and material_prim.GetPath() == MaterialType.MATERIAL_SELECTED:

                    UsdShade.MaterialBindingAPI(prim).UnbindDirectBinding()
                    try:
                        self._hightlighted_prims.remove(prim_path)
                    except ValueError:
                        pass
                else:
                    mtl = UsdShade.Material.Get(stage, Sdf.Path(MaterialType.MATERIAL_SELECTED))
                    prim.GetPrim().ApplyAPI(UsdShade.MaterialBindingAPI)
                    UsdShade.MaterialBindingAPI(prim).Bind(mtl)
                    UsdShade.MaterialBindingAPI(prim).SetMaterialBindingStrength(prim.GetAuthoredProperties()[0], UsdShade.Tokens.strongerThanDescendants)
                    self._hightlighted_prims.append(prim_path)

        if set(old_hightlighted_prims).symmetric_difference(self._hightlighted_prims).length > 0:
            Messenger().push(Messenger.EVENT_HIGHTLIGHTED_PRIMS_CHANGED, {
                'old': old_hightlighted_prims,
                'new': self._hightlighted_prims
            })

    def get_hightlighted_prims(self):
        return self._hightlighted_prims

    @staticmethod
    def setup_materials():
        context = omni.usd.get_context()
        stage = context.get_stage()

        # Create Error Overlay Material
        prim = stage.GetPrimAtPath(Sdf.Path(MaterialType.MATERIAL_ERROR))
        if str(prim) == Constants.INVALID_NULL_PRIM:
            mtl_path = Sdf.Path(MaterialType.MATERIAL_ERROR)
            mtl = UsdShade.Material.Define(stage, mtl_path)
            shader = UsdShade.Shader.Define(stage, mtl_path.AppendPath("Shader"))
            shader.CreateIdAttr("UsdPreviewSurface")
            shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((1.0, 0.0, 0.0))
            shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.5)
            shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)

            mtl.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")


        prim = stage.GetPrimAtPath(Sdf.Path(MaterialType.MATERIAL_SELECTED))
        if str(prim) == Constants.INVALID_NULL_PRIM:
            # Create Selected part Overlay Material
            mtl_path = Sdf.Path(MaterialType.MATERIAL_SELECTED)
            mtl = UsdShade.Material.Define(stage, mtl_path)
            shader = UsdShade.Shader.Define(stage, mtl_path.AppendPath("Shader"))
            shader.CreateIdAttr("UsdPreviewSurface")
            shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((0.0, 0.964, 1.0))
            shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.5)
            shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
            mtl.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")