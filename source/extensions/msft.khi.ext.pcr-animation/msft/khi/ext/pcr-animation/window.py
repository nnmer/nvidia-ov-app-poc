__all__ = ["MsftKhiAnimationWindow"]
import omni.ui as ui
import os, tempfile
import carb
from omni.kit.viewport.utility import get_active_viewport_window

from msft.ext.adt import Messenger, style

from .alert_viewport_widget import *
from .widget_nyokkey import NyokkeyWidget
from .widget_twins_list import TwinsListWidget
from .viewport_widgets_store import ViewportWidgetsStore
from msft.ext.adt import ADT, AdtPullingRegistry, MeshMaterials
from msft.ext.viewport_widgets_manager import WidgetAlignment, AlertWidgetProvider
import msft.ext.viewport_widgets_manager as ViewportWidgetsManager

class MsftKhiAnimationWindow(ui.Window):
    """MsftKhiAnimationWindow"""

    title = "Dashboard"
    msg = None
    label_msg_adt = None
    label_msg_signalr = None
    # _widget_info_viewport1 = None
    # _widget_info_viewport2 = None

    def __init__(self, **kwargs):
        super().__init__(MsftKhiAnimationWindow.title, **kwargs)
        self._nyokkey_widget = NyokkeyWidget()
        self._twins_list_widget = TwinsListWidget()
        self.draw_ui()

        AdtPullingRegistry().register_action('register_location_samples_adt_pull_action', self.register_location_samples_adt_pull_action, 5)
        AdtPullingRegistry().start_action('register_location_samples_adt_pull_action')

    def draw_ui(self):
        # here you build the content of the window
        with self.frame:
            with ui.VStack(height=0):
                if os.environ["OV_DEFAULT_STAGE_LOAD"] and bool(os.environ["OV_STAGE_AUTOLOAD"]) == False:
                    ui.Button('Load stage', clicked_fn=self._load_and_setup_stage, style=style)
                ui.Spacer(height=10)
                # with ui.HStack(height=0):
                ui.Label(os.environ["OV_AZURE_DIGITALTWINS_ROOT_NODE_ID"], style={"font_size": 24})
                ui.Label("In oper. status", style={"font_size": 12})

                ui.Label("TBD: List alerts here if any", style={"font_size": 12, "color": ui.color(256,100,100)})

                ui.Spacer(height=10)
                with ui.HStack():
                    with ui.ZStack():
                        ui.Rectangle(width=200, height=100, style={"background_color": ui.color("#000000")})
                        with ui.VStack(height=0):
                            ui.Spacer(height=4)
                            ui.Label("Samples", style={"font_size": 24})
                            self.label_samples_number = ui.Label("", style={"font_size": 32})

                    self._nyokkey_widget.render()

                self._twins_list_widget.render()

                ui.Spacer(height=20)
                self.msg = ui.Label('Controlls TBD')
                self.btn = ui.Button('Show WidgetWindow Error',clicked_fn=self.create_alert_widget3)
                self.btn = ui.Button('Clean all WidgetWindow',clicked_fn=ViewportWidgetsStore().clean_all)
                self.btn = ui.Button('Show Manipulator widget',clicked_fn=self.create_alert_widget1)
                ui.Spacer(height=20)
                self.label_msg_adt = ui.Label('')
                ui.Spacer(height=20)
                self.label_msg_signalr = ui.Label('',word_wrap=True)

        if os.environ["OV_STAGE_AUTOLOAD"] == 'true':
            self._load_and_setup_stage()

    def register_location_samples_adt_pull_action(self):
        query_expression = f"SELECT * FROM digitaltwins dt WHERE dt.$dtId = 'Overall_Control_PLC_Haneda'"
        query_result = ADT().service_client().query_twins(query_expression)
        for i in query_result:
            if bool(os.environ['OV_DEBUG']):
                carb.log_info(f"[Samples] pulled data => {i}")
            # carb.log_warn(f" ==register_location_samples_adt_pull_action==> Item {i['NumberOfInputSamples']} , {id(i)}")
            val = str(i['NumberOfInputSamples'])
            self.label_samples_number.text = val+'-'+str(id(i))[-7:] if bool(os.environ["OV_DEV"]) == True else val

        # infoWidget = RobotInfoWidgetProvider()
        # ViewportWidgetManager.add_widget('/World/khi_rs007n_vac_UNIT1', infoWidget, WidgetAlignment.CENTER)


        # alertWidget = RobotAlertWidgetProvider()
        # ViewportWidgetManager.add_widget('/World/khi_rs007n_vac_UNIT3', alertWidget, WidgetAlignment.TOP)

        # infoWidget = RobotInfoWidgetProvider()
        # ViewportWidgetManager.add_widget('/World/khi_rs007n_vac_UNIT3', infoWidget, WidgetAlignment.CENTER)


        # alertWidget = RobotAlertWidgetProvider()
        # ViewportWidgetManager.add_widget('/World/khi_rs007n_vac_UNIT4', alertWidget, WidgetAlignment.TOP)

        # infoWidget = RobotInfoWidgetProvider()
        # ViewportWidgetManager.add_widget('/World/khi_rs007n_vac_UNIT4', infoWidget, WidgetAlignment.CENTER)
    def create_alert_widget3(self):
        mesh_id = '/World/khi_rs007n_vac_UNIT1'

        alertWidget = AlertWidgetProvider(f"AAAAAAA broke broke broke.....do something....")
        widget_id = ViewportWidgetsManager.add_widget(mesh_id, alertWidget, WidgetAlignment.TOP)
        ViewportWidgetsStore().set(mesh_id, widget_id)

    def create_alert_widget1(self):
        # Get the active (which at startup is the default Viewport)
        viewport_window = get_active_viewport_window()

        # Issue an error if there is no Viewport
        if not viewport_window:
            carb.log_warn(f"No Viewport Window to add {'abc'} scene to")
            self._widget_info_viewport1 = None
            return

        # Build out the scene
        self._widget_info_viewport1 = AlertViewportWidget(viewport_window, 'abc', {
            '/World/khi_rs007n_vac_UNIT4',
            '/World/khi_rs007n_vac_UNIT3',
            '/World/khi_rs007n_vac_UNIT2',
            '/World/khi_rs007n_vac_UNIT1'
        })

        ctx = omni.usd.get_context()
        ctx.get_selection().set_selected_prim_paths(['/World/khi_rs007n_vac_UNIT3'], True)


    def _load_and_setup_stage(self):

        # update_stream = omni.kit.app.get_app().get_update_event_stream()

        # def on_update(e: carb.events.IEvent):
        #     print(f"Update: {e.payload['dt']}")
        usd_ctx = omni.usd.get_context()

        def setup_layers():
            new_layer_id = 'origin'     # uuid.uuid4()
            stage = usd_ctx.get_stage()
            tmp_folder = tempfile.gettempdir()
            omni.kit.commands.execute("CreateSublayer",
                layer_identifier=stage.GetRootLayer().identifier,
                # This example prepends to the subLayers list
                sublayer_position=1,
                new_layer_path=rf"{tmp_folder}{os.sep}{new_layer_id}.usd",
                layer_name="Origin",
                transfer_root_content=True,
                # When True, it will create the layer file for you too.
                create_or_insert=True
            )

            new_layer_id = 'msft.adt.workspace-overlay'  #uuid.uuid4()
            omni.kit.commands.execute("CreateSublayer",
                layer_identifier=stage.GetRootLayer().identifier,
                # This example prepends to the subLayers list
                sublayer_position=0,
                new_layer_path=rf"{tmp_folder}{os.sep}{new_layer_id}.usd",
                layer_name="Animation",
                transfer_root_content=False,
                # When True, it will create the layer file for you too.
                create_or_insert=True
            )

            omni.kit.commands.execute('SetEditTarget',
                layer_identifier=f"{tmp_folder}{os.sep}{new_layer_id}.usd",
            )

        def finish_setup(arg1, arg2):
            setup_layers()
            MeshMaterials.setup_materials()
            Messenger().push(Messenger().EVENT_LOADING_COMPLETED)

        stage2load = os.environ["OV_DEFAULT_STAGE_LOAD"]
        if stage2load and len(stage2load) > 0 and (os.path.exists(stage2load) or stage2load.startswith('omniverse:')):
            usd_ctx.open_stage_with_callback(
                stage2load,
                on_finish_fn=finish_setup
            )

        # sub = update_stream.create_subscription_to_pop(on_update, name="My Subscription Name")

    # def create_alert_widget1(self):
    #     ref_handler = self._widget_info_viewport1
    #     self.create_alert_widget(ref_handler, 'abc', ['/World/khi_rs007n_vac_UNIT3'])
    # def create_alert_widget2(self):
    #     ref_handler = self._widget_info_viewport2
    #     self.create_alert_widget(ref_handler, 'xyz', ['/World/khi_rs007n_vac_UNIT4'])

    # def create_alert_widget(self, ref_handler, ext_id, prim_path):
    #     # Get the active (which at startup is the default Viewport)
    #     viewport_window = get_active_viewport_window()

    #     # Issue an error if there is no Viewport
    #     if not viewport_window:
    #         carb.log_warn(f"No Viewport Window to add {ext_id} scene to")
    #         ref_handler = None
    #         return

    #     # Build out the scene
    #     ref_handler = AlertViewportWidget(viewport_window, ext_id, {
    #         '/World/khi_rs007n_vac_UNIT4',
    #         '/World/khi_rs007n_vac_UNIT3',
    #         '/World/khi_rs007n_vac_UNIT2',
    #         '/World/khi_rs007n_vac_UNIT1'
    #     })

    #     ctx = omni.usd.get_context()
    #     ctx.get_selection().set_selected_prim_paths(prim_path, True)

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False
