import omni.usd
import carb
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
        pass

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
        context = omni.usd.get_context()
        stage = context.get_stage()

        prim_paths = self._get_context().get_selection().get_selected_prim_paths()
        for prim_path in prim_paths:
            carb.log_info(f"adt selected prim {prim_path}")

            prim = stage.GetPrimAtPath(prim_path)
            mtl = UsdShade.Material.Get(stage, Sdf.Path(MaterialType.MATERIAL_SELECTED))
            prim.GetPrim().ApplyAPI(UsdShade.MaterialBindingAPI)
            UsdShade.MaterialBindingAPI(prim).Bind(mtl)
            UsdShade.MaterialBindingAPI(prim).SetMaterialBindingStrength(prim.GetAuthoredProperties()[0], UsdShade.Tokens.strongerThanDescendants)

            for key in prim.GetCustomData():
                print(f' — {key} = {prim.GetCustomDataByKey(key)}')

    @staticmethod
    def setup_materials():
        context = omni.usd.get_context()
        stage = context.get_stage()

        # Create Error Overlay Material
        prim = stage.GetPrimAtPath(Sdf.Path(MaterialType.MATERIAL_ERROR))
        if str(prim) == 'invalid null prim':
            mtl_path = Sdf.Path(MaterialType.MATERIAL_ERROR)
            mtl = UsdShade.Material.Define(stage, mtl_path)
            shader = UsdShade.Shader.Define(stage, mtl_path.AppendPath("Shader"))
            shader.CreateIdAttr("UsdPreviewSurface")
            shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((1.0, 0.0, 0.0))
            shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.5)
            shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)

            mtl.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")


        prim = stage.GetPrimAtPath(Sdf.Path(MaterialType.MATERIAL_SELECTED))
        if str(prim) == 'invalid null prim':
            # Create Selected part Overlay Material
            mtl_path = Sdf.Path(MaterialType.MATERIAL_SELECTED)
            mtl = UsdShade.Material.Define(stage, mtl_path)
            shader = UsdShade.Shader.Define(stage, mtl_path.AppendPath("Shader"))
            shader.CreateIdAttr("UsdPreviewSurface")
            shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((0.0, 0.964, 1.0))
            shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.5)
            shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
            mtl.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")